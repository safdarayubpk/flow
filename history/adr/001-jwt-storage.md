# ADR-001: JWT Token Storage Method for Secure Web Application

## Status
Accepted

## Context
The application requires secure storage of JWT tokens after user authentication in a web application with frontend-backend separation. The choice of storage method directly impacts security against XSS and CSRF attacks, user experience, and cross-origin implications. This decision affects how the frontend will handle authentication state and how tokens are transmitted with API requests.

## Decision
Store JWT tokens in httpOnly/Secure cookies for maximum security against XSS attacks while maintaining usability. This approach ensures that JWT tokens are not accessible to client-side JavaScript, preventing theft via XSS vulnerabilities, while still allowing automatic transmission with API requests.

## Alternatives Considered
- **localStorage**: Pro: Easy to access from JavaScript, persistent storage; Con: Vulnerable to XSS attacks that can steal tokens
- **sessionStorage**: Pro: Available during browser session, not persistent; Con: Still vulnerable to XSS, lost when tab closes
- **httpOnly/Secure cookies**: Pro: Protected against XSS attacks, automatic transmission with requests; Con: Potential CSRF vulnerability if not properly mitigated

## Rationale
The httpOnly cookie approach was selected because security is paramount in a multi-user application where data isolation is critical. While localStorage is more commonly used in SPAs, the risk of token theft through XSS attacks outweighs the convenience. The CSRF risk can be mitigated with proper CSRF tokens, whereas XSS protection for stored tokens is impossible once they're in client-side storage.

## Consequences
- **Positive**: Enhanced security against XSS attacks, automatic token inclusion with requests
- **Negative**: Requires additional CSRF protection mechanisms, potential complexity with cross-origin requests
- **Constraints**: Need to implement proper CSRF tokens, careful configuration of SameSite attribute