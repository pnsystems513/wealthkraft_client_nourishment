# ─── Email Templates ──────────────────────────────────────────────────────────

import base64
import os

# ── Load images as base64 (used as inline CID attachments, NOT data-URIs) ────
_IMAGES_DIR = os.path.join(os.path.dirname(__file__), "images")

def _b64_img(filename: str) -> str:
    """Return a Base64-encoded string for the given image file."""
    path = os.path.join(_IMAGES_DIR, filename)
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")

# Pre-load at import time so they're ready for every send
WELCOME_IMG_B64  = _b64_img("welcome.jpeg")
BIRTHDAY_IMG_B64 = _b64_img("birthday.jpeg")

# CID keys referenced in HTML as  src="cid:<key>"
WELCOME_IMG_CID  = "welcome_banner"
BIRTHDAY_IMG_CID = "birthday_banner"


# ─── Welcome Template ─────────────────────────────────────────────────────────

def _welcome_html(client_name: str) -> str:
    first_name = client_name.split()[0] if client_name else "there"
    return f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
      <meta charset="UTF-8" />
      <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
      <title>Welcome to WealthKraft</title>
    </head>
    <body style="margin:0;padding:0;background:#f4f7fb;font-family:'Segoe UI',Arial,sans-serif;">
      <table width="100%" cellpadding="0" cellspacing="0" style="background:#f4f7fb;padding:40px 0;">
        <tr>
          <td align="center">
            <table width="600" cellpadding="0" cellspacing="0" style="background:#ffffff;border-radius:12px;overflow:hidden;box-shadow:0 4px 24px rgba(0,0,0,0.08);">

              <!-- Hero Image (CID inline attachment) -->
              <tr>
                <td style="padding:0;line-height:0;">
                  <img src="cid:{WELCOME_IMG_CID}"
                       alt="Welcome to the WealthKraft Family"
                       width="600"
                       style="display:block;width:100%;max-width:600px;height:auto;border:0;" />
                </td>
              </tr>

              <!-- Body -->
              <tr>
                <td style="padding:40px 48px;">
                  <p style="margin:0 0 16px;color:#37474f;font-size:17px;line-height:1.7;">
                    Dear <strong>{first_name}</strong>,
                  </p>
                  <p style="margin:0 0 16px;color:#546e7a;font-size:15px;line-height:1.8;">
                    Thank you for placing your trust in us. We are delighted to be a part of your wealth creation journey.
                  </p>
                  <p style="margin:0 0 16px;color:#546e7a;font-size:15px;line-height:1.8;">
                    At <strong>WealthKraft</strong>, we believe that successful investing is not about chasing quick returns—it's about
                    building wealth patiently, consistently, and peacefully. Our goal is to help you make informed financial decisions
                    that bring you closer to your dreams and long-term financial freedom.
                  </p>

                  <!-- What to expect -->
                  <p style="margin:0 0 12px;color:#37474f;font-size:15px;font-weight:600;">Here's what you can expect from us:</p>
                  <table width="100%" cellpadding="0" cellspacing="0" style="margin-bottom:24px;">
                    <tr>
                      <td style="background:#e8f5e9;border-radius:8px;padding:16px 20px;width:21%;">
                        <p style="margin:0;font-size:22px;text-align:center;">📊</p>
                        <p style="margin:8px 0 0;color:#2e7d32;font-size:13px;text-align:center;font-weight:600;">Regular Portfolio Reviews</p>
                      </td>
                      <td style="width:3%;"></td>
                      <td style="background:#e3f2fd;border-radius:8px;padding:16px 20px;width:21%;">
                        <p style="margin:0;font-size:22px;text-align:center;">📰</p>
                        <p style="margin:8px 0 0;color:#1565c0;font-size:13px;text-align:center;font-weight:600;">Timely Market Insights</p>
                      </td>
                      <td style="width:3%;"></td>
                      <td style="background:#fce4ec;border-radius:8px;padding:16px 20px;width:21%;">
                        <p style="margin:0;font-size:22px;text-align:center;">🤝</p>
                        <p style="margin:8px 0 0;color:#c62828;font-size:13px;text-align:center;font-weight:600;">Dedicated Support</p>
                      </td>
                      <td style="width:3%;"></td>
                      <td style="background:#fff8e1;border-radius:8px;padding:16px 20px;width:21%;">
                        <p style="margin:0;font-size:22px;text-align:center;">💡</p>
                        <p style="margin:8px 0 0;color:#e65100;font-size:13px;text-align:center;font-weight:600;">Transparent Guidance</p>
                      </td>
                    </tr>
                  </table>

                  <!-- Quote -->
                  <table width="100%" cellpadding="0" cellspacing="0" style="margin-bottom:24px;">
                    <tr>
                      <td style="background:linear-gradient(135deg,#e8eaf6,#e3f2fd);border-radius:12px;padding:20px 24px;text-align:center;border-left:4px solid #1a237e;">
                        <p style="margin:0;color:#1a237e;font-size:15px;font-style:italic;font-weight:600;line-height:1.6;">
                          &ldquo;Time in the market is more powerful than timing the market.&rdquo;
                        </p>
                      </td>
                    </tr>
                  </table>

                  <p style="margin:0 0 16px;color:#546e7a;font-size:15px;line-height:1.8;">
                    Your investment journey begins today, and every disciplined step you take brings you closer to a financially secure future.
                  </p>
                  <p style="margin:0 0 16px;color:#546e7a;font-size:15px;line-height:1.8;">
                    Thank you once again for choosing <strong>WealthKraft</strong>. We look forward to building your wealth—peacefully.
                  </p>
                  <p style="margin:24px 0 0;color:#37474f;font-size:15px;line-height:1.7;">
                    Warm Regards,<br/>
                    <strong>Ketan Mali</strong><br/>
                    <span style="color:#1565c0;">Founder, WealthKraft</span><br/>
                    <em style="color:#90a4ae;font-size:13px;">Building Wealth in the Peaceful Way.</em>
                  </p>
                </td>
              </tr>

              <!-- Footer -->
              <tr>
                <td style="background:#f8f9fa;padding:24px 48px;text-align:center;border-top:1px solid #eceff1;">
                  <p style="margin:0;color:#90a4ae;font-size:12px;">
                    &copy; 2024 WealthKraft. All rights reserved.
                  </p>
                  <p style="margin:4px 0 0;color:#90a4ae;font-size:12px;">
                    This email was sent as part of your onboarding process.
                  </p>
                </td>
              </tr>

            </table>
          </td>
        </tr>
      </table>
    </body>
    </html>
    """


# ─── Birthday Template ────────────────────────────────────────────────────────

def _birthday_html(client_name: str) -> str:
    first_name = client_name.split()[0] if client_name else "there"
    return f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
      <meta charset="UTF-8" />
      <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
      <title>Happy Birthday from WealthKraft</title>
    </head>
    <body style="margin:0;padding:0;background:#f4f7fb;font-family:'Segoe UI',Arial,sans-serif;">
      <table width="100%" cellpadding="0" cellspacing="0" style="background:#f4f7fb;padding:40px 0;">
        <tr>
          <td align="center">
            <table width="600" cellpadding="0" cellspacing="0" style="background:#ffffff;border-radius:12px;overflow:hidden;box-shadow:0 4px 24px rgba(0,0,0,0.08);">

              <!-- Hero Image (CID inline attachment) -->
              <tr>
                <td style="padding:0;line-height:0;">
                  <img src="cid:{BIRTHDAY_IMG_CID}"
                       alt="Happy Birthday from WealthKraft"
                       width="600"
                       style="display:block;width:100%;max-width:600px;height:auto;border:0;" />
                </td>
              </tr>

              <!-- Body -->
              <tr>
                <td style="padding:40px 48px;">
                  <p style="margin:0 0 16px;color:#37474f;font-size:16px;line-height:1.8;">
                    Dear <strong>{first_name}</strong>,
                  </p>
                  <p style="margin:0 0 16px;color:#37474f;font-size:16px;line-height:1.8;">
                    Wishing you a very <strong>Happy Birthday!</strong> 🎉
                  </p>
                  <p style="margin:0 0 16px;color:#546e7a;font-size:15px;line-height:1.8;">
                    May this new year of your life bring you good health, happiness, prosperity, and countless reasons to celebrate.
                  </p>
                  <p style="margin:0 0 24px;color:#546e7a;font-size:15px;line-height:1.8;">
                    Just as every birthday marks another milestone in life, every year of disciplined investing brings you one step
                    closer to financial freedom. The greatest gift you can give your future self is to stay invested, stay patient,
                    and let the power of compounding work for you.
                  </p>

                  <!-- Quote box -->
                  <table width="100%" cellpadding="0" cellspacing="0" style="margin-bottom:24px;">
                    <tr>
                      <td style="background:linear-gradient(135deg,#f3e5f5,#fce4ec);border-radius:12px;padding:24px;text-align:center;border-left:4px solid #7b1fa2;">
                        <p style="margin:0;font-size:28px;">🎊 🥳 🎁</p>
                        <p style="margin:12px 0 0;color:#6a1b9a;font-size:16px;font-weight:600;line-height:1.6;font-style:italic;">
                          &ldquo;The best investments are not measured in days or months,<br/>but in years of patience and discipline.&rdquo;
                        </p>
                      </td>
                    </tr>
                  </table>

                  <p style="margin:0 0 16px;color:#546e7a;font-size:15px;line-height:1.8;">
                    Thank you for trusting <strong>WealthKraft</strong> to be a part of your wealth creation journey.
                    We remain committed to helping you build a secure and prosperous future.
                  </p>
                  <p style="margin:0 0 16px;color:#546e7a;font-size:15px;line-height:1.8;">
                    Have a wonderful celebration!
                  </p>
                  <p style="margin:24px 0 0;color:#37474f;font-size:15px;line-height:1.7;">
                    Warm Wishes,<br/>
                    <strong>Ketan Mali</strong><br/>
                    <span style="color:#7b1fa2;">Founder, WealthKraft</span><br/>
                    <em style="color:#90a4ae;font-size:13px;">Building Wealth in the Peaceful Way.</em>
                  </p>
                </td>
              </tr>

              <!-- Footer -->
              <tr>
                <td style="background:#f8f9fa;padding:24px 48px;text-align:center;border-top:1px solid #eceff1;">
                  <p style="margin:0;color:#90a4ae;font-size:12px;">
                    &copy; 2024 WealthKraft. All rights reserved.
                  </p>
                  <p style="margin:4px 0 0;color:#90a4ae;font-size:12px;">
                    You're receiving this because you are a valued WealthKraft client.
                  </p>
                </td>
              </tr>

            </table>
          </td>
        </tr>
      </table>
    </body>
    </html>
    """
