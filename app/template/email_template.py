# ─── Email Templates ──────────────────────────────────────────────────────────

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

              <!-- Header -->
              <tr>
                <td style="background:linear-gradient(135deg,#1a237e 0%,#1565c0 100%);padding:40px 48px;text-align:center;">
                  <h1 style="margin:0;color:#ffffff;font-size:28px;font-weight:700;letter-spacing:-0.5px;">
                    Welcome to WealthKraft 🎉
                  </h1>
                  <p style="margin:8px 0 0;color:#bbdefb;font-size:15px;">
                    Your wealth journey starts here
                  </p>
                </td>
              </tr>

              <!-- Body -->
              <tr>
                <td style="padding:40px 48px;">
                  <p style="margin:0 0 16px;color:#37474f;font-size:17px;line-height:1.7;">
                    Hi <strong>{first_name}</strong>,
                  </p>
                  <p style="margin:0 0 16px;color:#546e7a;font-size:15px;line-height:1.8;">
                    We're thrilled to have you on board as part of the <strong>WealthKraft</strong> family.
                    Your financial goals are now in expert hands.
                  </p>
                  <p style="margin:0 0 24px;color:#546e7a;font-size:15px;line-height:1.8;">
                    Your dedicated advisor will be reaching out shortly to understand your financial
                    aspirations and craft a personalised strategy just for you.
                  </p>

                  <!-- Highlights -->
                  <table width="100%" cellpadding="0" cellspacing="0" style="margin-bottom:24px;">
                    <tr>
                      <td style="background:#e8f5e9;border-radius:8px;padding:16px 20px;width:30%;">
                        <p style="margin:0;font-size:22px;text-align:center;">📊</p>
                        <p style="margin:8px 0 0;color:#2e7d32;font-size:13px;text-align:center;font-weight:600;">Portfolio Tracking</p>
                      </td>
                      <td style="width:4%;"></td>
                      <td style="background:#e3f2fd;border-radius:8px;padding:16px 20px;width:30%;">
                        <p style="margin:0;font-size:22px;text-align:center;">🛡️</p>
                        <p style="margin:8px 0 0;color:#1565c0;font-size:13px;text-align:center;font-weight:600;">Risk Management</p>
                      </td>
                      <td style="width:4%;"></td>
                      <td style="background:#fce4ec;border-radius:8px;padding:16px 20px;width:30%;">
                        <p style="margin:0;font-size:22px;text-align:center;">🎯</p>
                        <p style="margin:8px 0 0;color:#c62828;font-size:13px;text-align:center;font-weight:600;">Goal Planning</p>
                      </td>
                    </tr>
                  </table>

                  <p style="margin:0;color:#546e7a;font-size:15px;line-height:1.8;">
                    If you have any questions in the meantime, feel free to reach out to us.
                    We look forward to building your financial future together.
                  </p>
                </td>
              </tr>

              <!-- Footer -->
              <tr>
                <td style="background:#f8f9fa;padding:24px 48px;text-align:center;border-top:1px solid #eceff1;">
                  <p style="margin:0;color:#90a4ae;font-size:12px;">
                    © 2024 WealthKraft. All rights reserved.
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

              <!-- Header -->
              <tr>
                <td style="background:linear-gradient(135deg,#4a148c 0%,#7b1fa2 60%,#e91e63 100%);padding:48px;text-align:center;">
                  <p style="margin:0;font-size:56px;line-height:1;">🎂</p>
                  <h1 style="margin:16px 0 0;color:#ffffff;font-size:30px;font-weight:700;">
                    Happy Birthday, {first_name}!
                  </h1>
                  <p style="margin:8px 0 0;color:#e1bee7;font-size:15px;">
                    Wishing you a wonderful day filled with joy
                  </p>
                </td>
              </tr>

              <!-- Body -->
              <tr>
                <td style="padding:40px 48px;">
                  <p style="margin:0 0 16px;color:#37474f;font-size:16px;line-height:1.8;">
                    On your special day, the entire WealthKraft team extends their warmest wishes to you. 🎉
                  </p>
                  <p style="margin:0 0 24px;color:#546e7a;font-size:15px;line-height:1.8;">
                    May this year bring you excellent health, abundant happiness, and outstanding
                    financial growth. We're proud to be a part of your wealth journey and
                    look forward to celebrating many more milestones together.
                  </p>

                  <!-- Birthday card box -->
                  <table width="100%" cellpadding="0" cellspacing="0">
                    <tr>
                      <td style="background:linear-gradient(135deg,#f3e5f5,#fce4ec);border-radius:12px;padding:24px;text-align:center;">
                        <p style="margin:0;font-size:28px;">🎊 🥳 🎁</p>
                        <p style="margin:12px 0 0;color:#6a1b9a;font-size:16px;font-weight:600;line-height:1.6;">
                          "The secret of getting ahead is getting started." <br/>
                          <span style="font-size:13px;font-weight:400;color:#8e24aa;">— Mark Twain</span>
                        </p>
                      </td>
                    </tr>
                  </table>

                  <p style="margin:24px 0 0;color:#546e7a;font-size:15px;line-height:1.8;">
                    Here's to another year of smart investments and financial freedom!
                  </p>
                </td>
              </tr>

              <!-- Footer -->
              <tr>
                <td style="background:#f8f9fa;padding:24px 48px;text-align:center;border-top:1px solid #eceff1;">
                  <p style="margin:0;color:#90a4ae;font-size:12px;">
                    © 2024 WealthKraft. All rights reserved.
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
