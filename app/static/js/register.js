function selectLevel(element) {
  document.querySelectorAll(".level-card").forEach((card) => {
    card.classList.remove("aqua-border", "bg-surface-bright");
    card.classList.add("border-transparent", "bg-surface-container");
  });
  element.classList.add("aqua-border", "bg-surface-bright");
  element.classList.remove("border-transparent", "bg-surface-container");
  document.getElementById("level").value = element.dataset.level;
}

function selectTime(time, element) {
  document.querySelectorAll(".time-btn").forEach((btn) => {
    btn.classList.remove("bg-primary-container", "text-white");
    btn.classList.add("text-on-surface-variant");
  });
  element.classList.add("bg-primary-container", "text-white");
  element.classList.remove("text-on-surface-variant");
  document.getElementById("time_preferred").value = time;
}

(function () {
  const form = document.getElementById("register-form");
  if (!form) return; // registration closed — nothing below applies

  const fullNameInput = form.querySelector('[name="full_name"]');
  const motherNameInput = form.querySelector('[name="mother_name"]');
  const phoneInput = form.querySelector('[name="phone"]');
  const dobInput = form.querySelector('[name="date_of_birth"]');

  const returningToggle = document.getElementById("returning-toggle");
  const returningPanel = document.getElementById("returning-panel");
  const participantNumberInput = document.getElementById("participant-number-input");
  const participantNumberSpinner = document.getElementById("participant-number-spinner");
  const participantNumberMessage = document.getElementById("participant-number-message");
  const returningClearBtn = document.getElementById("returning-clear");

  const errorBanner = document.getElementById("form-error-banner");
  const confirmedParticipantIdInput = document.getElementById("confirmed_participant_id");
  const skipDuplicateCheckInput = document.getElementById("skip_duplicate_check");

  const submitBtn = document.getElementById("register-submit-btn");
  const submitLabel = document.getElementById("register-submit-label");
  const submitSpinner = document.getElementById("register-submit-spinner");
  const submitIcon = document.getElementById("register-submit-icon");

  const confirmDialog = document.getElementById("duplicate-confirm-dialog");
  const confirmMessage = document.getElementById("duplicate-confirm-message");
  const confirmYesBtn = document.getElementById("duplicate-confirm-yes");
  const confirmNoBtn = document.getElementById("duplicate-confirm-no");

  const LOCKED_CLASSES = ["bg-surface-container", "text-on-surface-variant"];
  let pendingMatchId = null;
  let participantLookupController = null;

  function formatDob(iso) {
    try {
      return new Date(`${iso}T00:00:00`).toLocaleDateString("en-US", {
        month: "short",
        day: "numeric",
        year: "numeric",
      });
    } catch (err) {
      return iso;
    }
  }

  function lockField(input, value) {
    input.value = value;
    input.readOnly = true;
    input.classList.add(...LOCKED_CLASSES);
    input.classList.remove("bg-surface-bright");
  }

  function unlockField(input) {
    input.readOnly = false;
    input.classList.remove(...LOCKED_CLASSES);
    input.classList.add("bg-surface-bright");
  }

  function fillLocked(data) {
    // Full Name and Date of Birth stay editable after autofill — parents can
    // still fix a typo or correct a birthdate. Mother's Name and Phone (the
    // verified factor) stay locked.
    fullNameInput.value = data.full_name;
    lockField(motherNameInput, data.mother_name);
    lockField(phoneInput, data.phone_local);
    dobInput.value = data.date_of_birth;
    returningClearBtn.classList.remove("hidden");
    // Ties the submission to this exact participant, so editing Full Name/DOB
    // above updates their existing record instead of creating a new one.
    confirmedParticipantIdInput.value = data.id;
  }

  function clearLocked() {
    [fullNameInput, motherNameInput, phoneInput, dobInput].forEach((input) => {
      unlockField(input);
      input.value = "";
    });
    returningClearBtn.classList.add("hidden");
    participantNumberInput.value = "";
    confirmedParticipantIdInput.value = "";
    setParticipantMessage("");
  }

  function setParticipantMessage(text, isError) {
    if (!text) {
      participantNumberMessage.classList.add("hidden");
      return;
    }
    participantNumberMessage.textContent = text;
    participantNumberMessage.classList.remove("hidden", "text-error", "text-secondary");
    participantNumberMessage.classList.add(isError ? "text-error" : "text-secondary");
  }

  // --- Returning participant shortcut ---
  returningToggle.addEventListener("click", () => {
    returningPanel.classList.toggle("hidden");
    if (!returningPanel.classList.contains("hidden")) participantNumberInput.focus();
  });

  returningClearBtn.addEventListener("click", clearLocked);

  // Both the Participant Number and the Phone Number are required to validate —
  // the number alone is sequential/guessable, so anyone could otherwise claim to
  // be a returning participant just by trying numbers. Only once both fields
  // have a value do we call the backend, which checks them together.
  async function lookupReturningParticipant() {
    const number = participantNumberInput.value.trim();
    const phone = phoneInput.value.trim();

    // Any lookup attempt invalidates a previously confirmed match until this
    // one succeeds — otherwise editing the number/phone after a match could
    // leave the submission silently tied to the wrong (stale) participant.
    confirmedParticipantIdInput.value = "";

    if (!number) {
      setParticipantMessage("");
      return;
    }
    if (!phone) {
      setParticipantMessage("Also enter your phone number below to verify it's you.", false);
      return;
    }

    if (participantLookupController) participantLookupController.abort();
    participantLookupController = new AbortController();
    participantNumberSpinner.classList.remove("hidden");
    setParticipantMessage("");

    try {
      const resp = await fetch(
        `/register/lookup/participant?number=${encodeURIComponent(number)}&phone=${encodeURIComponent(phone)}`,
        { signal: participantLookupController.signal }
      );
      const data = await resp.json();
      if (data.found) {
        fillLocked(data);
        setParticipantMessage("Loaded your details below.", false);
      } else {
        setParticipantMessage("We couldn't verify those details. Check your participant number and phone number.", true);
      }
    } catch (err) {
      if (err.name !== "AbortError") setParticipantMessage("Couldn't check that right now.", true);
    } finally {
      participantNumberSpinner.classList.add("hidden");
    }
  }

  participantNumberInput.addEventListener("blur", lookupReturningParticipant);
  participantNumberInput.addEventListener("keydown", (e) => {
    if (e.key === "Enter") {
      e.preventDefault();
      lookupReturningParticipant();
    }
  });

  // Phone is the second factor for the returning-participant shortcut above —
  // once both it and the Participant Number have a value, validate the pair.
  phoneInput.addEventListener("blur", () => {
    if (phoneInput.readOnly) return; // already verified via the returning-participant shortcut
    if (!returningPanel.classList.contains("hidden") && participantNumberInput.value.trim()) {
      lookupReturningParticipant();
    }
  });

  // --- Error banner ---
  function showError(message) {
    errorBanner.textContent = message;
    errorBanner.classList.remove("hidden");
    errorBanner.scrollIntoView({ behavior: "smooth", block: "nearest" });
  }

  function hideError() {
    errorBanner.classList.add("hidden");
  }

  // --- Submit spinner state ---
  function setSubmitting(isSubmitting) {
    submitBtn.disabled = isSubmitting;
    submitLabel.classList.toggle("hidden", isSubmitting);
    submitSpinner.classList.toggle("hidden", !isSubmitting);
    submitIcon.classList.toggle("hidden", isSubmitting);
  }

  // --- Confirmation modal ---
  function showConfirmDialog(match) {
    pendingMatchId = match.id;
    confirmMessage.textContent = `It looks like you may have registered before as ${match.full_name}, born ${formatDob(
      match.date_of_birth
    )}. Is this the same person?`;
    confirmDialog.showModal();
  }

  confirmYesBtn.addEventListener("click", () => {
    confirmedParticipantIdInput.value = pendingMatchId;
    skipDuplicateCheckInput.value = "";
    confirmDialog.close();
    submitForm();
  });

  confirmNoBtn.addEventListener("click", () => {
    confirmedParticipantIdInput.value = "";
    skipDuplicateCheckInput.value = "1";
    confirmDialog.close();
    submitForm();
  });

  // --- Form submission ---
  async function submitForm() {
    setSubmitting(true);
    hideError();
    try {
      const resp = await fetch(form.action, { method: "POST", body: new FormData(form) });
      const data = await resp.json();
      if (data.redirect_url) {
        window.location.href = data.redirect_url;
        return; // leave submitting state as-is — we're navigating away
      }
      if (data.needs_confirmation) {
        showConfirmDialog(data.match);
      } else if (data.error) {
        showError(data.error);
      } else {
        showError("Something went wrong. Please try again.");
      }
    } catch (err) {
      showError("Network error. Please check your connection and try again.");
    } finally {
      setSubmitting(false);
    }
  }

  form.addEventListener("submit", (e) => {
    e.preventDefault();
    // Don't clear confirmed_participant_id here — it may have been set by the
    // returning-participant shortcut above, which must survive into this
    // submit so the backend updates that participant instead of creating a
    // new one. skip_duplicate_check is a true one-shot (only ever set right
    // before the confirmation modal's own resubmit, never via this handler).
    skipDuplicateCheckInput.value = "";
    submitForm();
  });
})();
