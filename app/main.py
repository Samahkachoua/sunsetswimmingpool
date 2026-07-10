from datetime import date, datetime, timedelta
from datetime import date as date_cls

from fastapi import APIRouter, Depends, FastAPI, Form, HTTPException, Request
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from postgrest.exceptions import APIError

from app.supabase_client import get_admin_user, sign_in_admin, supabase

app = FastAPI(title="Sunset Swimming Pool")

app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

SESSION_COOKIE = "sb_access_token"


class NotAuthenticated(Exception):
    pass


@app.exception_handler(NotAuthenticated)
def not_authenticated_handler(request: Request, exc: NotAuthenticated):
    response = RedirectResponse(url=f"/admin/login?next={request.url.path}", status_code=303)
    response.delete_cookie(SESSION_COOKIE)
    return response


def require_admin(request: Request) -> None:
    token = request.cookies.get(SESSION_COOKIE)
    if not token:
        raise NotAuthenticated()
    try:
        get_admin_user(token)
    except Exception:
        raise NotAuthenticated()


admin_router = APIRouter(dependencies=[Depends(require_admin)])

STATUS_BADGE_CLASSES = {
    "pending": "bg-tertiary-fixed/20 text-on-tertiary-fixed-variant",
    "confirmed": "bg-secondary-container/20 text-on-secondary-container",
    "completed": "bg-surface-container-high text-on-surface-variant",
}

RESERVATION_STATUS_CLASSES = {
    "pending": "bg-tertiary-fixed/20 text-on-tertiary-fixed-variant",
    "confirmed": "bg-secondary/10 text-secondary",
    "cancelled": "bg-error-container/50 text-on-error-container",
}


def format_time_range(starts_at_iso: str, ends_at_iso: str) -> str:
    def fmt(dt: datetime) -> str:
        hour = dt.hour % 12 or 12
        ampm = "AM" if dt.hour < 12 else "PM"
        return f"{hour}:{dt.minute:02d} {ampm}"

    start = datetime.fromisoformat(starts_at_iso)
    end = datetime.fromisoformat(ends_at_iso)
    return f"{fmt(start)} - {fmt(end)}"


def calculate_age(birth_date_str: str) -> int:
    birth_date = date.fromisoformat(birth_date_str)
    today = date.today()
    return today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))


@app.get("/")
def index(request: Request):
    return templates.TemplateResponse(request, "index.html")


@app.get("/healthz")
def healthz():
    return {"status": "ok"}


@app.get("/register")
def register_form(request: Request):
    open_cycles = (
        supabase.table("cycles")
        .select("id, name, start_date, end_date")
        .eq("is_open_for_registration", True)
        .order("start_date")
        .execute()
        .data
    )
    return templates.TemplateResponse(request, "register.html", {"open_cycles": open_cycles})


@app.post("/register")
def register_submit(
    full_name: str = Form(...),
    mother_name: str = Form(...),
    phone: str = Form(...),
    date_of_birth: date = Form(...),
    level: str = Form(...),
    time_preferred: str = Form(...),
    cycle_id: int = Form(...),
):
    participant = (
        supabase.table("participants")
        .insert({
            "full_name": full_name,
            "mother_name": mother_name,
            "phone": f"+961 {phone}",
            "date_of_birth": date_of_birth.isoformat(),
        })
        .execute()
        .data[0]
    )

    enrollment = (
        supabase.table("enrollments")
        .insert({
            "participant_id": participant["id"],
            "cycle_id": cycle_id,
            "level": level,
            "time_preferred": time_preferred,
            "price": 0,
        })
        .execute()
        .data[0]
    )

    return RedirectResponse(url=f"/register/success/{enrollment['id']}", status_code=303)


@app.get("/register/success/{enrollment_id}")
def register_success(request: Request, enrollment_id: int):
    enrollment = (
        supabase.table("enrollments")
        .select("id, level, time_preferred, status, participants(full_name), cycles(name, start_date, end_date)")
        .eq("id", enrollment_id)
        .single()
        .execute()
        .data
    )
    if enrollment is None:
        raise HTTPException(status_code=404)
    return templates.TemplateResponse(request, "register_success.html", {"enrollment": enrollment})


def _safe_next_path(next_path: str) -> str:
    if next_path.startswith("/") and not next_path.startswith("//"):
        return next_path
    return "/admin/dashboard"


@app.get("/admin/login")
def admin_login_form(request: Request, next: str = "/admin/dashboard"):
    next = _safe_next_path(next)
    if request.cookies.get(SESSION_COOKIE):
        return RedirectResponse(url=next, status_code=303)
    return templates.TemplateResponse(request, "admin/login.html", {"next": next, "error": None})


@app.post("/admin/login")
def admin_login_submit(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    next: str = Form("/admin/dashboard"),
):
    next = _safe_next_path(next)
    try:
        auth_response = sign_in_admin(email, password)
    except Exception:
        return templates.TemplateResponse(
            request,
            "admin/login.html",
            {"next": next, "error": "Invalid email or password."},
            status_code=401,
        )

    response = RedirectResponse(url=next, status_code=303)
    response.set_cookie(
        SESSION_COOKIE,
        auth_response.session.access_token,
        max_age=auth_response.session.expires_in,
        httponly=True,
        samesite="lax",
    )
    return response


@app.post("/admin/logout")
def admin_logout():
    response = RedirectResponse(url="/admin/login", status_code=303)
    response.delete_cookie(SESSION_COOKIE)
    return response


@admin_router.get("/admin/dashboard")
def admin_dashboard(request: Request):
    enrollments = (
        supabase.table("enrollments")
        .select("id, level, status, created_at, participants(full_name)")
        .order("created_at", desc=True)
        .execute()
        .data
    )
    total_reservations = supabase.table("reservations").select("id", count="exact").execute().count

    level_counts = {"beginner": 0, "intermediate": 0, "advanced": 0}
    pending_enrollments = 0
    for enrollment in enrollments:
        if enrollment["level"] in level_counts:
            level_counts[enrollment["level"]] += 1
        if enrollment["status"] == "pending":
            pending_enrollments += 1
        enrollment["created_at_display"] = datetime.fromisoformat(enrollment["created_at"]).strftime("%B %d, %Y")

    return templates.TemplateResponse(
        request,
        "admin/dashboard.html",
        {
            "today": date.today().strftime("%B %d, %Y"),
            "total_enrollments": len(enrollments),
            "pending_enrollments": pending_enrollments,
            "total_reservations": total_reservations,
            "level_counts": level_counts,
            "recent_enrollments": enrollments[:10],
            "status_classes": STATUS_BADGE_CLASSES,
        },
    )


@admin_router.get("/admin/cycles")
def admin_cycles(request: Request):
    cycles = (
        supabase.table("cycles")
        .select("id, name, start_date, end_date, is_open_for_registration")
        .order("start_date", desc=True)
        .execute()
        .data
    )
    return templates.TemplateResponse(
        request,
        "admin/cycles.html",
        {"cycles": cycles, "error": request.query_params.get("error")},
    )


@admin_router.post("/admin/cycles")
def admin_cycles_create(
    name: str = Form(...),
    start_date: date = Form(...),
    end_date: date = Form(...),
    is_open_for_registration: bool = Form(False),
):
    try:
        supabase.table("cycles").insert({
            "name": name,
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "is_open_for_registration": is_open_for_registration,
        }).execute()
    except APIError as exc:
        if exc.code == "23P01":
            error = "Those dates overlap an existing cycle. Pick a date range that doesn't conflict."
        else:
            error = "Could not create the cycle."
        return RedirectResponse(url=f"/admin/cycles?error={error}", status_code=303)
    return RedirectResponse(url="/admin/cycles", status_code=303)


@admin_router.post("/admin/cycles/{cycle_id}/toggle-open")
def admin_cycles_toggle_open(cycle_id: int):
    cycle = (
        supabase.table("cycles")
        .select("is_open_for_registration")
        .eq("id", cycle_id)
        .single()
        .execute()
        .data
    )
    supabase.table("cycles").update(
        {"is_open_for_registration": not cycle["is_open_for_registration"]}
    ).eq("id", cycle_id).execute()
    return RedirectResponse(url="/admin/cycles", status_code=303)


@admin_router.post("/admin/cycles/{cycle_id}/delete")
def admin_cycles_delete(cycle_id: int):
    try:
        supabase.table("cycles").delete().eq("id", cycle_id).execute()
    except APIError:
        return RedirectResponse(
            url="/admin/cycles?error=Cannot delete a cycle that has enrollments.",
            status_code=303,
        )
    return RedirectResponse(url="/admin/cycles", status_code=303)


@admin_router.get("/admin/participants")
def admin_participants(request: Request):
    participants = (
        supabase.table("participants")
        .select("id, full_name, mother_name, phone, date_of_birth")
        .order("full_name")
        .execute()
        .data
    )
    for participant in participants:
        participant["age"] = calculate_age(participant["date_of_birth"])

    return templates.TemplateResponse(
        request,
        "admin/participants.html",
        {"participants": participants, "error": request.query_params.get("error")},
    )


@admin_router.post("/admin/participants/{participant_id}/edit")
def admin_participants_edit(
    participant_id: int,
    full_name: str = Form(...),
    mother_name: str = Form(...),
    phone: str = Form(...),
    date_of_birth: date = Form(...),
):
    supabase.table("participants").update({
        "full_name": full_name,
        "mother_name": mother_name,
        "phone": phone,
        "date_of_birth": date_of_birth.isoformat(),
    }).eq("id", participant_id).execute()
    return RedirectResponse(url="/admin/participants", status_code=303)


@admin_router.post("/admin/participants/{participant_id}/delete")
def admin_participants_delete(participant_id: int):
    supabase.table("participants").delete().eq("id", participant_id).execute()
    return RedirectResponse(url="/admin/participants", status_code=303)


@admin_router.get("/admin/enrollments")
def admin_enrollments(request: Request):
    enrollments = (
        supabase.table("enrollments")
        .select("id, level, time_preferred, price, status, participants(full_name, date_of_birth)")
        .order("created_at", desc=True)
        .execute()
        .data
    )
    payments = (
        supabase.table("payments")
        .select("payable_id, amount")
        .eq("payable_type", "enrollment")
        .execute()
        .data
    )
    paid_by_enrollment = {}
    for payment in payments:
        paid_by_enrollment[payment["payable_id"]] = (
            paid_by_enrollment.get(payment["payable_id"], 0) + payment["amount"]
        )

    for enrollment in enrollments:
        enrollment["age"] = calculate_age(enrollment["participants"]["date_of_birth"])
        enrollment["paid"] = paid_by_enrollment.get(enrollment["id"], 0)

    return templates.TemplateResponse(
        request,
        "admin/enrollments.html",
        {
            "enrollments": enrollments,
            "status_classes": STATUS_BADGE_CLASSES,
            "today_iso": date.today().isoformat(),
            "error": request.query_params.get("error"),
        },
    )


@admin_router.post("/admin/enrollments/{enrollment_id}/edit")
def admin_enrollments_edit(
    enrollment_id: int,
    time_preferred: str = Form(...),
    level: str = Form(...),
    status: str = Form(...),
    price: float = Form(...),
):
    try:
        supabase.table("enrollments").update({
            "time_preferred": time_preferred,
            "level": level,
            "status": status,
            "price": price,
        }).eq("id", enrollment_id).execute()
    except APIError:
        return RedirectResponse(
            url="/admin/enrollments?error=Could not save changes. The status value may not be recognized by the database.",
            status_code=303,
        )
    return RedirectResponse(url="/admin/enrollments", status_code=303)


@admin_router.post("/admin/enrollments/{enrollment_id}/record-payment")
def admin_enrollments_record_payment(
    enrollment_id: int,
    amount: float = Form(...),
    paid_at: date = Form(...),
    method: str = Form(...),
    notes: str = Form(""),
):
    supabase.table("payments").insert({
        "payable_type": "enrollment",
        "payable_id": enrollment_id,
        "amount": amount,
        "method": method,
        "paid_at": paid_at.isoformat(),
        "notes": notes or None,
    }).execute()
    return RedirectResponse(url="/admin/enrollments", status_code=303)


@admin_router.post("/admin/enrollments/{enrollment_id}/delete")
def admin_enrollments_delete(enrollment_id: int):
    supabase.table("enrollments").delete().eq("id", enrollment_id).execute()
    return RedirectResponse(url="/admin/enrollments", status_code=303)


@admin_router.get("/admin/reservations")
def admin_reservations(request: Request, date: str | None = None):
    pools = supabase.table("pools").select("id, name").order("name").execute().data
    selected_date = date_cls.fromisoformat(date) if date else date_cls.today()

    if not pools:
        return templates.TemplateResponse(
            request,
            "admin/reservations.html",
            {"pools": pools, "error": request.query_params.get("error")},
        )

    day_start = datetime.combine(selected_date, datetime.min.time()).isoformat()
    day_end = datetime.combine(selected_date + timedelta(days=1), datetime.min.time()).isoformat()

    reservations = (
        supabase.table("reservations")
        .select("id, pool_id, customer_name, customer_phone, starts_at, ends_at, price_snapshot, status")
        .gte("starts_at", day_start)
        .lt("starts_at", day_end)
        .order("starts_at")
        .execute()
        .data
    )
    reservations_by_pool: dict[int, list] = {}
    for reservation in reservations:
        reservation["time_range"] = format_time_range(reservation["starts_at"], reservation["ends_at"])
        reservations_by_pool.setdefault(reservation["pool_id"], []).append(reservation)

    return templates.TemplateResponse(
        request,
        "admin/reservations.html",
        {
            "pools": pools,
            "reservations_by_pool": reservations_by_pool,
            "status_classes": RESERVATION_STATUS_CLASSES,
            "display_date": selected_date.strftime("%B %d, %Y"),
            "weekday_name": selected_date.strftime("%A"),
            "iso_date": selected_date.isoformat(),
            "prev_date": (selected_date - timedelta(days=1)).isoformat(),
            "next_date": (selected_date + timedelta(days=1)).isoformat(),
            "error": request.query_params.get("error"),
        },
    )


@admin_router.post("/admin/reservations")
def admin_reservations_create(
    pool_id: int = Form(...),
    customer_name: str = Form(...),
    customer_phone: str = Form(...),
    res_date: date_cls = Form(...),
    start_time: str = Form(...),
    end_time: str = Form(...),
    status: str = Form("pending"),
):
    day_type = "weekend" if res_date.weekday() >= 5 else "weekday"
    pricing_rule = (
        supabase.table("pricing_rules")
        .select("price")
        .eq("pool_id", pool_id)
        .eq("day_type", day_type)
        .limit(1)
        .execute()
        .data
    )
    price = pricing_rule[0]["price"] if pricing_rule else 0

    starts_at = f"{res_date.isoformat()}T{start_time}:00"
    ends_at = f"{res_date.isoformat()}T{end_time}:00"

    try:
        supabase.table("reservations").insert({
            "pool_id": pool_id,
            "customer_name": customer_name,
            "customer_phone": f"+961 {customer_phone}",
            "starts_at": starts_at,
            "ends_at": ends_at,
            "price_snapshot": price,
            "status": status,
        }).execute()
    except APIError:
        return RedirectResponse(
            url=f"/admin/reservations?date={res_date.isoformat()}&error=Could not create reservation. Check the status value.",
            status_code=303,
        )
    return RedirectResponse(url=f"/admin/reservations?date={res_date.isoformat()}", status_code=303)


@admin_router.get("/admin/settings")
def admin_settings(request: Request):
    pools = supabase.table("pools").select("id, name, capacity, is_active").order("name").execute().data
    pricing_rules = supabase.table("pricing_rules").select("pool_id, day_type, price").execute().data

    prices_by_pool: dict[int, dict[str, float]] = {}
    for rule in pricing_rules:
        prices_by_pool.setdefault(rule["pool_id"], {})[rule["day_type"]] = rule["price"]

    for pool in pools:
        pool["weekday_price"] = prices_by_pool.get(pool["id"], {}).get("weekday")
        pool["weekend_price"] = prices_by_pool.get(pool["id"], {}).get("weekend")

    return templates.TemplateResponse(
        request,
        "admin/settings.html",
        {"pools": pools, "error": request.query_params.get("error")},
    )


@admin_router.post("/admin/settings/pools")
def admin_settings_create_pool(name: str = Form(...), capacity: int = Form(...)):
    supabase.table("pools").insert({"name": name, "capacity": capacity}).execute()
    return RedirectResponse(url="/admin/settings", status_code=303)


@admin_router.post("/admin/settings/pools/{pool_id}/toggle-active")
def admin_settings_toggle_pool_active(pool_id: int):
    pool = supabase.table("pools").select("is_active").eq("id", pool_id).single().execute().data
    supabase.table("pools").update({"is_active": not pool["is_active"]}).eq("id", pool_id).execute()
    return RedirectResponse(url="/admin/settings", status_code=303)


def _upsert_pricing_rule(pool_id: int, day_type: str, price: float) -> None:
    existing = (
        supabase.table("pricing_rules")
        .select("id")
        .eq("pool_id", pool_id)
        .eq("day_type", day_type)
        .execute()
        .data
    )
    if existing:
        supabase.table("pricing_rules").update({"price": price}).eq("id", existing[0]["id"]).execute()
    else:
        supabase.table("pricing_rules").insert(
            {"pool_id": pool_id, "day_type": day_type, "price": price}
        ).execute()


@admin_router.post("/admin/settings/pools/{pool_id}/pricing")
def admin_settings_update_pricing(
    pool_id: int,
    weekday_price: float = Form(...),
    weekend_price: float = Form(...),
):
    _upsert_pricing_rule(pool_id, "weekday", weekday_price)
    _upsert_pricing_rule(pool_id, "weekend", weekend_price)
    return RedirectResponse(url="/admin/settings", status_code=303)


app.include_router(admin_router)
