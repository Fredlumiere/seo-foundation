// Optional Basic Auth gate for the Vercel-hosted audit dashboard.
// Delete this file if the dashboard should be public.
// Set AUDIT_USER and AUDIT_PASSWORD as Vercel project env vars (Production scope).

export const config = {
  matcher: ['/((?!_next/|_vercel/|favicon\\.ico).*)'],
  runtime: 'edge',
};

function timingSafeEqual(a, b) {
  if (a.length !== b.length) return false;
  let result = 0;
  for (let i = 0; i < a.length; i++) {
    result |= a.charCodeAt(i) ^ b.charCodeAt(i);
  }
  return result === 0;
}

export default function middleware(request) {
  const expectedUser = process.env.AUDIT_USER || '{project}';
  const expectedPwd = process.env.AUDIT_PASSWORD;

  if (!expectedPwd) {
    return new Response('Audit dashboard misconfigured: AUDIT_PASSWORD not set', {
      status: 500,
    });
  }

  const auth = request.headers.get('authorization');
  if (auth) {
    const [scheme, encoded] = auth.split(' ');
    if (scheme === 'Basic' && encoded) {
      try {
        const decoded = atob(encoded);
        const [user, pwd] = decoded.split(':');
        if (timingSafeEqual(user || '', expectedUser) && timingSafeEqual(pwd || '', expectedPwd)) {
          return;
        }
      } catch {}
    }
  }

  return new Response('Authentication required', {
    status: 401,
    headers: { 'WWW-Authenticate': `Basic realm="{project} audit"` },
  });
}
