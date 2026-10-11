"""
MH Club E-Commerce Presentation Generator
Generates a Classic, Clean, Executive 12-slide presentation in PPTX format.
Design Philosophy: Minimalist, High-Impact, Executive Corporate (No Clutter, Crisp Whitespace).
"""
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

def create_presentation(output_path="MH_Club_Executive_Presentation.pptx"):
    prs = Presentation()
    # 16:9 Widescreen dimensions
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6]

    # Classic Corporate Color Palette
    BG_LIGHT = RGBColor(248, 250, 252)     # Clean Crisp Slate-50 (#F8FAFC)
    BG_WHITE = RGBColor(255, 255, 255)     # Pure White (#FFFFFF)
    CARD_BORDER = RGBColor(226, 232, 240)  # Slate-200 Border (#E2E8F0)
    
    PRIMARY_NAVY = RGBColor(15, 23, 42)    # Deep Executive Navy (#0F172A)
    PRIMARY_BLUE = RGBColor(30, 58, 138)   # Classic Blue (#1E3A8A)
    ACCENT_INDIGO = RGBColor(79, 70, 229)  # Refined Indigo (#4F46E5)
    ACCENT_EMERALD = RGBColor(5, 150, 105) # Professional Emerald (#059669)
    ACCENT_AMBER = RGBColor(217, 119, 6)   # Refined Amber (#D97706)
    ACCENT_ROSE = RGBColor(225, 29, 72)    # Classic Crimson/Rose (#E11D48)
    
    TEXT_DARK = RGBColor(15, 23, 42)       # Slate-900 (#0F172A)
    TEXT_MUTED = RGBColor(71, 85, 105)     # Slate-600 (#475569)
    TEXT_LIGHT = RGBColor(148, 163, 184)   # Slate-400 (#94A3B8)

    def set_slide_background(slide, color=BG_LIGHT):
        bg = slide.shapes.add_shape(
            MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), prs.slide_width, prs.slide_height
        )
        bg.fill.solid()
        bg.fill.fore_color.rgb = color
        bg.line.fill.background()
        return bg

    def add_classic_header(slide, slide_num, category, title):
        set_slide_background(slide)

        # Top Category Tag
        cat_box = slide.shapes.add_textbox(Inches(0.9), Inches(0.55), Inches(8.0), Inches(0.3))
        tf_c = cat_box.text_frame
        tf_c.word_wrap = True
        p_c = tf_c.paragraphs[0]
        p_c.text = category.upper()
        p_c.font.size = Pt(10)
        p_c.font.bold = True
        p_c.font.color.rgb = ACCENT_INDIGO

        # Slide Number
        num_box = slide.shapes.add_textbox(Inches(10.5), Inches(0.55), Inches(1.9), Inches(0.3))
        tf_n = num_box.text_frame
        p_n = tf_n.paragraphs[0]
        p_n.text = f"{slide_num:02d} / 12"
        p_n.alignment = PP_ALIGN.RIGHT
        p_n.font.size = Pt(10)
        p_n.font.bold = True
        p_n.font.color.rgb = TEXT_LIGHT

        # Slide Title
        title_box = slide.shapes.add_textbox(Inches(0.9), Inches(0.82), Inches(11.5), Inches(0.7))
        tf_t = title_box.text_frame
        tf_t.word_wrap = True
        p_t = tf_t.paragraphs[0]
        p_t.text = title
        p_t.font.size = Pt(24)
        p_t.font.bold = True
        p_t.font.color.rgb = PRIMARY_NAVY

        # Subtle Header Underline
        line = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.9), Inches(1.52), Inches(11.533), Inches(0.02))
        line.fill.solid()
        line.fill.fore_color.rgb = CARD_BORDER
        line.line.fill.background()

    def add_classic_card(slide, left, top, width, height, title, points, accent_color=PRIMARY_BLUE, tag=""):
        # White Card
        card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
        card.fill.solid()
        card.fill.fore_color.rgb = BG_WHITE
        card.line.color.rgb = CARD_BORDER
        card.line.width = Pt(1)

        # Left Accent Stripe
        stripe = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, Inches(0.08), height)
        stripe.fill.solid()
        stripe.fill.fore_color.rgb = accent_color
        stripe.line.fill.background()

        # Title & Optional Tag
        tb = slide.shapes.add_textbox(left + Inches(0.25), top + Inches(0.2), width - Inches(0.5), Inches(0.45))
        tf = tb.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = title
        p.font.size = Pt(14)
        p.font.bold = True
        p.font.color.rgb = PRIMARY_NAVY

        # Concise Points
        content_tb = slide.shapes.add_textbox(left + Inches(0.25), top + Inches(0.65), width - Inches(0.5), height - Inches(0.8))
        ctf = content_tb.text_frame
        ctf.word_wrap = True
        for i, pt in enumerate(points):
            p_item = ctf.paragraphs[0] if i == 0 else ctf.add_paragraph()
            p_item.text = f"•  {pt}"
            p_item.font.size = Pt(11.5)
            p_item.font.color.rgb = TEXT_MUTED
            p_item.space_after = Pt(8)

    def add_metric_pill(slide, left, top, width, height, value, label, color=ACCENT_INDIGO):
        card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
        card.fill.solid()
        card.fill.fore_color.rgb = BG_WHITE
        card.line.color.rgb = CARD_BORDER
        card.line.width = Pt(1)

        tb = slide.shapes.add_textbox(left + Inches(0.15), top + Inches(0.1), width - Inches(0.3), height - Inches(0.2))
        tf = tb.text_frame
        tf.word_wrap = True
        p1 = tf.paragraphs[0]
        p1.text = value
        p1.font.size = Pt(20)
        p1.font.bold = True
        p1.font.color.rgb = color

        p2 = tf.add_paragraph()
        p2.text = label
        p2.font.size = Pt(11)
        p2.font.bold = True
        p2.font.color.rgb = PRIMARY_NAVY
        p2.space_before = Pt(2)

    # ==========================================
    # SLIDE 1: TITLE SLIDE (CLASSIC EXECUTIVE)
    # ==========================================
    s1 = prs.slides.add_slide(blank_layout)
    set_slide_background(s1, BG_WHITE)

    # Decorative Top Accent Bar
    top_bar = s1.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), prs.slide_width, Inches(0.1))
    top_bar.fill.solid()
    top_bar.fill.fore_color.rgb = PRIMARY_BLUE
    top_bar.line.fill.background()

    # Brand Title Box
    title_box = s1.shapes.add_textbox(Inches(1.2), Inches(1.8), Inches(11.0), Inches(2.2))
    tf1 = title_box.text_frame
    tf1.word_wrap = True
    
    p_tag = tf1.paragraphs[0]
    p_tag.text = "FULL-STACK E-COMMERCE & LAST-MILE LOGISTICS PLATFORM"
    p_tag.font.size = Pt(12)
    p_tag.font.bold = True
    p_tag.font.color.rgb = ACCENT_INDIGO

    p_title = tf1.add_paragraph()
    p_title.text = "MH CLUB"
    p_title.font.size = Pt(44)
    p_title.font.bold = True
    p_title.font.color.rgb = PRIMARY_NAVY
    p_title.space_before = Pt(8)

    p_sub = tf1.add_paragraph()
    p_sub.text = "A Complete Retail Ecosystem: Multi-Variant Inventory, Razorpay Payments & OTP Delivery"
    p_sub.font.size = Pt(16)
    p_sub.font.color.rgb = TEXT_MUTED
    p_sub.space_before = Pt(6)

    # 4 Clean Metric / Pillar Cards
    pillars = [
        ("Python & Django 5", "MVC Backend & REST APIs", PRIMARY_BLUE),
        ("Razorpay + COD", "Dual Payment & Instant Refund", ACCENT_EMERALD),
        ("OTP Delivery Proof", "Zero Dispute Fulfillment", ACCENT_AMBER),
        ("Unfold Intelligence", "Real-Time KPI Command Center", ACCENT_INDIGO),
    ]
    for idx, (p_h, p_s, p_col) in enumerate(pillars):
        bx = Inches(1.2 + idx * 2.75)
        by = Inches(4.5)
        p_card = s1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, bx, by, Inches(2.55), Inches(1.25))
        p_card.fill.solid()
        p_card.fill.fore_color.rgb = BG_LIGHT
        p_card.line.color.rgb = CARD_BORDER
        p_card.line.width = Pt(1)

        p_tb = s1.shapes.add_textbox(bx + Inches(0.15), by + Inches(0.18), Inches(2.25), Inches(0.9))
        ptf = p_tb.text_frame
        ptf.word_wrap = True
        pp1 = ptf.paragraphs[0]
        pp1.text = p_h
        pp1.font.size = Pt(12.5)
        pp1.font.bold = True
        pp1.font.color.rgb = p_col

        pp2 = ptf.add_paragraph()
        pp2.text = p_s
        pp2.font.size = Pt(10)
        pp2.font.color.rgb = TEXT_MUTED
        pp2.space_before = Pt(3)

    # Bottom Presenter Footer
    foot_box = s1.shapes.add_textbox(Inches(1.2), Inches(6.3), Inches(11.0), Inches(0.4))
    tf_f = foot_box.text_frame
    pf = tf_f.paragraphs[0]
    pf.text = "Project Presentation  |  Stack: Python · Django · Razorpay · ReportLab · ApexCharts"
    pf.font.size = Pt(10.5)
    pf.font.color.rgb = TEXT_LIGHT

    # ==========================================
    # SLIDE 2: PROJECT OVERVIEW & CORE OBJECTIVES
    # ==========================================
    s2 = prs.slides.add_slide(blank_layout)
    add_classic_header(s2, 2, "Platform Overview", "Project Mission & Core Capabilities")

    add_classic_card(s2, Inches(0.9), Inches(1.85), Inches(5.6), Inches(2.4),
                     "Customer Experience", [
                         "Fuzzy live search with sub-50ms instant suggestions",
                         "Interactive multi-size variant picker with stock badges",
                         "Persistent shopping cart with saved delivery addresses",
                         "Transparent visual order timeline with 5-day returns"
                     ], ACCENT_INDIGO)

    add_classic_card(s2, Inches(6.8), Inches(1.85), Inches(5.6), Inches(2.4),
                     "Logistics & Fulfillment", [
                         "Role-isolated portal for delivery fleet drivers",
                         "Dynamic 6-digit OTP verification at customer doorstep",
                         "5-minute strict expiration timer preventing fraud",
                         "Real-time driver performance and cash tracking"
                     ], ACCENT_AMBER)

    add_classic_card(s2, Inches(0.9), Inches(4.55), Inches(5.6), Inches(2.4),
                     "Financial & Billing Automation", [
                         "Razorpay Online Payments + Cash on Delivery support",
                         "Cryptographic HMAC-SHA256 signature verification",
                         "Automated 1-click gateway refunds via Razorpay API",
                         "Dynamic ReportLab A4 PDF tax invoice generation"
                     ], ACCENT_EMERALD)

    add_classic_card(s2, Inches(6.8), Inches(4.55), Inches(5.6), Inches(2.4),
                     "Executive Intelligence & Security", [
                         "Django Unfold Control Center with animated KPI metrics",
                         "Interactive ApexCharts 7-day and 30-day sales trends",
                         "Proactive low-stock (≤ 5) and out-of-stock monitoring",
                         "Centralized Global Exception handling for 400/403/404/500"
                     ], PRIMARY_BLUE)

    # ==========================================
    # SLIDE 3: PROBLEM VS. SOLUTION
    # ==========================================
    s3 = prs.slides.add_slide(blank_layout)
    add_classic_header(s3, 3, "Problem & Solution", "Industry Bottlenecks vs. The MH Club Solution")

    add_classic_card(s3, Inches(0.9), Inches(1.85), Inches(5.6), Inches(5.0),
                     "Conventional E-Commerce Pain Points", [
                         "Courier Delivery Fraud: Fake 'customer unavailable' claims cause 8-12% dispute losses",
                         "Multi-Size Inventory Race Conditions: Overselling identical sizes during flash traffic",
                         "Manual Refund Latency: Tracing bank reconciliations manually takes 7-14 days",
                         "Disconnected Delivery Fleets: Couriers lack dedicated portals and OTP verification",
                         "Admin Blindspots: Generic backends lack real-time charts and stock auditing"
                     ], ACCENT_ROSE)

    add_classic_card(s3, Inches(6.8), Inches(1.85), Inches(5.6), Inches(5.0),
                     "The MH Club Architectural Solution", [
                         "Cryptographic OTP Delivery: 100% verified fulfillment via 6-digit email token",
                         "Atomic Database Locking: transaction.atomic() prevents size overselling",
                         "Automated 1-Click Refunds: Instant API refund dispatch directly from Admin",
                         "Dedicated Courier Dashboard: Mobile-first manifest with OTP input & cash logs",
                         "Unfold Command Suite: Live KPI counters, ApexCharts trends, and auto-invoices"
                     ], ACCENT_EMERALD)

    # ==========================================
    # SLIDE 4: SYSTEM ARCHITECTURE & TECH STACK
    # ==========================================
    s4 = prs.slides.add_slide(blank_layout)
    add_classic_header(s4, 4, "System Architecture", "Full-Stack Technology Architecture")

    add_classic_card(s4, Inches(0.9), Inches(1.85), Inches(3.6), Inches(5.0),
                     "Backend & Core", [
                         "Python 3.x Environment",
                         "Django 5.2.6 MVC Framework",
                         "Django REST Framework APIs",
                         "WhiteNoise 6.8.2 Static Caching",
                         "Gunicorn Multi-Worker WSGI",
                         "ACID Relational Database"
                     ], PRIMARY_BLUE)

    add_classic_card(s4, Inches(4.85), Inches(1.85), Inches(3.6), Inches(5.0),
                     "Frontend & Visuals", [
                         "Custom Vanilla CSS System",
                         "Bootstrap 5.3 Framework",
                         "AOS Scroll Animation Library",
                         "ApexCharts Data Visualizations",
                         "Inter & Jakarta Typography",
                         "Mobile-First Responsive Layouts"
                     ], ACCENT_INDIGO)

    add_classic_card(s4, Inches(8.8), Inches(1.85), Inches(3.6), Inches(5.0),
                     "Integrations & Services", [
                         "Razorpay Payment Gateway",
                         "HMAC-SHA256 Cryptography",
                         "ReportLab 4.4.7 PDF Engine",
                         "Multi-Threaded Async SMTP",
                         "Django Unfold Suite",
                         "Global Exception Middleware"
                     ], ACCENT_EMERALD)

    # ==========================================
    # SLIDE 5: USER ECOSYSTEM & RBAC
    # ==========================================
    s5 = prs.slides.add_slide(blank_layout)
    add_classic_header(s5, 5, "User Ecosystem", "Role-Based Access Control & User Journeys")

    add_classic_card(s5, Inches(0.9), Inches(1.85), Inches(3.6), Inches(5.0),
                     "1. End Shopper", [
                         "Live instant search suggestions",
                         "Multi-size variant stock picker",
                         "Persistent cart with address memory",
                         "Razorpay online or Cash on Delivery",
                         "Live status timeline & 5-day return"
                     ], ACCENT_INDIGO)

    add_classic_card(s5, Inches(4.85), Inches(1.85), Inches(3.6), Inches(5.0),
                     "2. Delivery Fleet Partner", [
                         "Dedicated route-isolated portal",
                         "Active customer delivery manifest",
                         "Doorstep 6-digit OTP trigger",
                         "OTP validation & auto-invoicing",
                         "Daily cash collection metrics"
                     ], ACCENT_AMBER)

    add_classic_card(s5, Inches(8.8), Inches(1.85), Inches(3.6), Inches(5.0),
                     "3. Store Admin & Ops", [
                         "Unfold statistical command center",
                         "Real-time gross revenue & order funnel",
                         "Multi-image & size variant editor",
                         "1-click gateway refund execution",
                         "Customer inquiries CRM manager"
                     ], PRIMARY_BLUE)

    # ==========================================
    # SLIDE 6: PRODUCT & INVENTORY ENGINE
    # ==========================================
    s6 = prs.slides.add_slide(blank_layout)
    add_classic_header(s6, 6, "Inventory Architecture", "Multi-Variant Catalog & Stock Engine")

    add_classic_card(s6, Inches(0.9), Inches(1.85), Inches(5.6), Inches(5.0),
                     "Relational Data Modeling", [
                         "Hierarchical Schema: Category → Subcategory → Product → ProductVariant",
                         "Size Variant Model: Independent stock quantities per size (S, M, L, XL, XXL)",
                         "Automated Discount Engine: Model save() hook calculates exact discount % from MRP",
                         "Multi-Image Galleries: ProductImage relations for multi-angle visual showcase",
                         "Dynamic Star Ratings: In-model validation enforcing 1 to 5 star ratings"
                     ], PRIMARY_BLUE)

    add_classic_card(s6, Inches(6.8), Inches(1.85), Inches(5.6), Inches(5.0),
                     "Stock Safety & Concurrency", [
                         "Database Atomic Transactions: Checkout locked inside transaction.atomic()",
                         "Zero Overselling: Real-time stock validation prevents race conditions",
                         "Auto Stock Restocking: Cancelled and returned items return to variant stock",
                         "Proactive Low-Stock Badging: Dashboard alerts for stock ≤ 5 and stock = 0",
                         "Optimized Querying: select_related & prefetch_related reduce DB queries by 75%"
                     ], ACCENT_INDIGO)

    # ==========================================
    # SLIDE 7: PAYMENTS & AUTOMATED REFUNDS
    # ==========================================
    s7 = prs.slides.add_slide(blank_layout)
    add_classic_header(s7, 7, "Financial Operations", "Dual Payment Engine & 1-Click Gateway Refunds")

    add_classic_card(s7, Inches(0.9), Inches(1.85), Inches(5.6), Inches(5.0),
                     "Payment Checkout & Verification", [
                         "Dual Mode Support: Razorpay (UPI, Cards, NetBanking) + Cash on Delivery",
                         "Server-Side Order Sync: Synchronizes Django Order ID with Razorpay Order ID",
                         "HMAC-SHA256 Verification: Cryptographic verification of payment signature",
                         "Tamper Defense: Failed signatures automatically flag order as 'Failed'",
                         "Order State Pipeline: Real-time status transitions (Pending → Paid → Dispatched)"
                     ], ACCENT_EMERALD)

    add_classic_card(s7, Inches(6.8), Inches(1.85), Inches(5.6), Inches(5.0),
                     "Automated 1-Click Gateway Refunds", [
                         "CancelledPaidOrder Model: Dedicated admin queue for refundable orders",
                         "Direct Razorpay Refund API: Integrated refund_payment() dispatches refunds in seconds",
                         "Optimum Speed Dispatch: Sent with speed: 'optimum' for rapid bank reversal",
                         "Audit Trail Logging: Records refund_id and updates timeline automatically",
                         "Zero Manual Errors: Eliminates manual bank tracing and administrative delays"
                     ], PRIMARY_BLUE)

    # ==========================================
    # SLIDE 8: OTP-VERIFIED LAST-MILE LOGISTICS
    # ==========================================
    s8 = prs.slides.add_slide(blank_layout)
    add_classic_header(s8, 8, "Logistics & Fulfillment", "OTP-Verified Proof-of-Delivery Workflow")

    steps = [
        ("1. Dispatch Assignment", "Admin assigns order to a delivery boy. Customer profile transitions to 'Out for Delivery'.", PRIMARY_BLUE),
        ("2. Doorstep OTP Trigger", "Agent arrives at customer doorstep and clicks 'Generate OTP' on mobile portal.", ACCENT_AMBER),
        ("3. 5-Min Expiry Email", "Customer receives styled HTML email with 6-digit code and total payable amount.", ACCENT_INDIGO),
        ("4. Verification & Invoice", "Agent enters OTP. System validates token, marks order Delivered, and auto-sends PDF invoice.", ACCENT_EMERALD),
    ]
    for idx, (s_title, s_desc, s_color) in enumerate(steps):
        bx = Inches(0.9 + idx * 2.95)
        by = Inches(1.85)
        s_card = s8.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, bx, by, Inches(2.75), Inches(3.2))
        s_card.fill.solid()
        s_card.fill.fore_color.rgb = BG_WHITE
        s_card.line.color.rgb = CARD_BORDER
        s_card.line.width = Pt(1)

        # Top Accent Stripe
        s_bar = s8.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, bx, by, Inches(2.75), Inches(0.08))
        s_bar.fill.solid()
        s_bar.fill.fore_color.rgb = s_color
        s_bar.line.fill.background()

        s_tb = s8.shapes.add_textbox(bx + Inches(0.15), by + Inches(0.2), Inches(2.45), Inches(2.8))
        stf = s_tb.text_frame
        stf.word_wrap = True
        sp1 = stf.paragraphs[0]
        sp1.text = s_title
        sp1.font.size = Pt(13)
        sp1.font.bold = True
        sp1.font.color.rgb = PRIMARY_NAVY

        sp2 = stf.add_paragraph()
        sp2.text = s_desc
        sp2.font.size = Pt(11)
        sp2.font.color.rgb = TEXT_MUTED
        sp2.space_before = Pt(8)

    add_metric_pill(s8, Inches(0.9), Inches(5.35), Inches(3.6), Inches(1.5), "5 Minutes", "Strict OTP Expiry Window", ACCENT_AMBER)
    add_metric_pill(s8, Inches(4.85), Inches(5.35), Inches(3.6), Inches(1.5), "0% Disputes", "Dispute-Free Fulfillment", ACCENT_EMERALD)
    add_metric_pill(s8, Inches(8.8), Inches(5.35), Inches(3.6), Inches(1.5), "Auto Invoice", "Dynamic ReportLab PDF Dispatch", PRIMARY_BLUE)

    # ==========================================
    # SLIDE 9: AUTOMATED INVOICE & ASYNC EMAIL
    # ==========================================
    s9 = prs.slides.add_slide(blank_layout)
    add_classic_header(s9, 9, "Billing & Communication", "Automated PDF Invoicing & Async Email Engine")

    add_classic_card(s9, Inches(0.9), Inches(1.85), Inches(5.6), Inches(5.0),
                     "ReportLab 4.4.7 Invoice Generation", [
                         "Dynamic A4 Vector Compilation: SimpleDocTemplate & Table flowables",
                         "Executive Brand Layout: MH Club canvas logo header and dark status bar",
                         "Itemized Line Items: Product Name, Size, Qty, MRP, Discount, and Total",
                         "Two-Column Details: Aligned billing & shipping address grids",
                         "In-Memory BytesIO Buffer: Zero disk I/O bottleneck, attached directly to email"
                     ], PRIMARY_BLUE)

    add_classic_card(s9, Inches(6.8), Inches(1.85), Inches(5.6), Inches(5.0),
                     "Multi-Threaded Async Email Engine", [
                         "Non-Blocking Architecture: send_email_async executed via threading.Thread",
                         "Account Activation: Secure Base64 UID + SHA-256 verification token links",
                         "Password Reset Protocol: Single-use PasswordResetTokenGenerator links",
                         "Delivery OTP Alerts: Styled HTML emails with bold 6-digit OTP boxes",
                         "Delivery Confirmation: Instant receipt with auto-attached PDF tax invoice"
                     ], ACCENT_INDIGO)

    # ==========================================
    # SLIDE 10: SECURITY & GLOBAL EXCEPTION HANDLING
    # ==========================================
    s10 = prs.slides.add_slide(blank_layout)
    add_classic_header(s10, 10, "Platform Resilience", "Enterprise Security & Global Exception Handling")

    add_classic_card(s10, Inches(0.9), Inches(1.85), Inches(5.6), Inches(5.0),
                     "Global Exception Middleware", [
                         "Centralized Fault Interception: Intercepts 400, 403, 404, and unhandled 500s",
                         "Luxury User Fallback: Renders clean custom error pages, hiding debug traces",
                         "Dual Mode API Output: Automatically returns clean JSON for AJAX / API calls",
                         "Static File Passthrough: Optimized passthrough for /static/ and /media/ routes",
                         "Catch-All Route: Fallback ensures broken URLs never expose framework errors"
                     ], ACCENT_ROSE)

    add_classic_card(s10, Inches(6.8), Inches(1.85), Inches(5.6), Inches(5.0),
                     "Role-Based Security & Protection", [
                         "DeliveryBoyRedirectMiddleware: Confines drivers strictly to delivery manifests",
                         "AuthUserRedirectMiddleware: Prevents logged-in users from duplicate auth forms",
                         "Cryptographic Tokens: Base64 + SHA-256 tokens for activation and password resets",
                         "CSRF & Webhook Defense: Django CSRF tokens + HMAC webhook verification",
                         "Password Complexity Suite: Multi-validator security enforcing strong credentials"
                     ], PRIMARY_BLUE)

    # ==========================================
    # SLIDE 11: 5-DAY RETURNS & REVERSE LOGISTICS
    # ==========================================
    s11 = prs.slides.add_slide(blank_layout)
    add_classic_header(s11, 11, "Reverse Logistics", "5-Day Return Engine & Doorstep Pickup")

    add_classic_card(s11, Inches(0.9), Inches(1.85), Inches(5.6), Inches(5.0),
                     "Dynamic 5-Day Return Window", [
                         "Timestamp Arithmetic: Return button enabled strictly for delivered_at + 5 days",
                         "Server Policy Enforcement: Backend rejects requests once the 5-day window closes",
                         "1-Click Customer Request: Initiated directly from profile order activity dashboard",
                         "Instant Fleet Dispatch: Order flagged is_returned=True and routed to driver manifest",
                         "Live Timeline Tracking: Customer profile updates to 'Return requested — assigned'"
                     ], ACCENT_AMBER)

    add_classic_card(s11, Inches(6.8), Inches(1.85), Inches(5.6), Inches(5.0),
                     "Doorstep Pickup & Stock Restoral", [
                         "Dedicated Returns Dashboard: Specialized portal (/delivery/return/) for pickups",
                         "1-Tap Pickup Confirmation: Delivery agent confirms pickup at doorstep",
                         "Automated Customer Notification: Instant email confirming successful pickup",
                         "Automatic Stock Restoration: Size variant inventory is restored automatically",
                         "1-Click Refund Trigger: Admin queues order for automated Razorpay/COD refund"
                     ], ACCENT_EMERALD)

    # ==========================================
    # SLIDE 12: BUSINESS VALUE & FUTURE ROADMAP
    # ==========================================
    s12 = prs.slides.add_slide(blank_layout)
    add_classic_header(s12, 12, "Impact & Vision", "Business Outcomes & Future Roadmap")

    add_classic_card(s12, Inches(0.9), Inches(1.85), Inches(5.6), Inches(5.0),
                     "Measurable Business Value Delivered", [
                         "0% Delivery Disputes: Dynamic OTP eliminates claims of missing deliveries",
                         "100% Stock Accuracy: Atomic database locking prevents duplicate orders",
                         "90% Faster Refunds: 1-click Razorpay refund cuts turnaround to < 10 seconds",
                         "100% Paperless Operations: Automated PDF invoice generation saves admin cost",
                         "High Customer Trust: Transparent timeline tracking and reliable 5-day returns"
                     ], ACCENT_EMERALD)

    add_classic_card(s12, Inches(6.8), Inches(1.85), Inches(5.6), Inches(5.0),
                     "Future Enhancement Roadmap", [
                         "AI-Powered Outfit Recommendations: Machine learning personalized styling",
                         "WhatsApp Cloud API Integration: Order alerts, OTPs, and tracking via WhatsApp",
                         "Multi-Warehouse Routing: Geolocation routing to fulfill from nearest hub",
                         "Progressive Web App (PWA): Offline browsing and fast mobile installation",
                         "24/7 AI Chatbot Assistant: Automated sizing advice and order query resolution"
                     ], PRIMARY_BLUE)

    # Save presentation
    prs.save(output_path)
    print(f"Classic presentation successfully created at: {output_path}")

if __name__ == "__main__":
    create_presentation()
