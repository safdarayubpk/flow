const pptxgen = require('pptxgenjs');
const path = require('path');
const html2pptx = require('../.claude/skills/pptx/scripts/html2pptx');

const SLIDES_DIR = path.join(__dirname, 'slides');
const SCREENSHOTS_DIR = path.join(__dirname, '..', 'todo-app-screenshots');
const ROOT = path.join(__dirname, '..');
const PHOTO = '/home/safdarayub/Desktop/Gemini_Generated_Image_9p6plc9p6plc9p6p.png';

async function create() {
  const pptx = new pptxgen();
  pptx.layout = 'LAYOUT_16x9';
  pptx.author = 'Safdar Ayub';
  pptx.title = 'Cloud-Native Todo App Deployment';

  // Slide 1: Title with photo
  const s1 = await html2pptx(path.join(SLIDES_DIR, 'slide01-title.html'), pptx);
  s1.slide.addImage({ path: PHOTO, x: 6.4, y: 0.75, w: 3.2, h: 3.2, rounding: true });
  s1.slide.addNotes('Welcome everyone. Today I will present the Cloud-Native Todo App deployment on Oracle Cloud OKE. This project demonstrates a full-stack deployment using modern cloud-native technologies on a free-tier cluster.');

  // Slide 2: Problem
  const s2 = await html2pptx(path.join(SLIDES_DIR, 'slide02-problem.html'), pptx);
  s2.slide.addNotes('The motivation was simple: we had a working local app but needed it accessible 24/7 from anywhere. The challenge was fitting everything - frontend, backend, Kafka, Dapr - into a single free-tier node with only 1 CPU and 8GB RAM.');

  // Slide 3: Architecture
  const s3 = await html2pptx(path.join(SLIDES_DIR, 'slide03-architecture.html'), pptx);
  s3.slide.addNotes('Here is the high-level architecture. The frontend is Next.js with Better Auth. The backend is FastAPI with a Dapr sidecar for pub/sub. Kafka handles event streaming. Everything runs on OCI OKE in Dubai region with Neon PostgreSQL as external database.');

  // Slide 4: Tech Stack
  const s4 = await html2pptx(path.join(SLIDES_DIR, 'slide04-techstack.html'), pptx);
  s4.slide.addNotes('Our tech stack includes 12 key technologies. Orange items are application-level: Next.js, FastAPI, Better Auth, Dapr. Blue items are infrastructure: Kafka, Neon PostgreSQL, Helm, OCI OKE. Green items are tooling: Docker, NGINX Ingress, Vercel as alternative frontend host, and Groq AI for the chat assistant.');

  // Slide 5: Challenges
  const s5 = await html2pptx(path.join(SLIDES_DIR, 'slide05-challenges.html'), pptx);
  s5.slide.addNotes('We encountered 5 major challenges. Kafka images from Bitnami and Confluent kept crashing - solved by switching to Apache Kafka with KRaft mode. MFA tokens expire hourly. The ingress regex rewrite broke frontend JS loading. Signup failed because the rewrite doubled the API prefix. And Dapr events silently failed because DAPR_ENABLED defaulted to False.');

  // Slide 6: Demo URLs
  const s6 = await html2pptx(path.join(SLIDES_DIR, 'slide06-demo-urls.html'), pptx);
  s6.slide.addNotes('The app is live at two URLs. The OKE deployment has the full stack including backend, Dapr, and Kafka at the IP address shown. Vercel hosts just the frontend with HTTPS and CDN. Both run 24/7 - the app does not depend on my laptop being on.');

  // Slide 7: Login Screenshot
  const s7 = await html2pptx(path.join(SLIDES_DIR, 'slide07-login.html'), pptx);
  s7.slide.addImage({
    path: path.join(SCREENSHOTS_DIR, 'Screenshot from 2026-02-19 16-13-03.png'),
    x: 3.95, y: 1.15, w: 5.7, h: 3.7
  });
  s7.slide.addNotes('This is the login page. It uses Better Auth for authentication with email and password. Each user gets their own isolated data - no user can see another users tasks.');

  // Slide 8: Dashboard Screenshot
  const s8 = await html2pptx(path.join(SLIDES_DIR, 'slide08-dashboard.html'), pptx);
  s8.slide.addImage({
    path: path.join(SCREENSHOTS_DIR, 'screencapture-139-185-51-243-tasks-2026-02-19-17_19_54.png'),
    x: 3.95, y: 1.1, w: 5.7, h: 3.85
  });
  s8.slide.addNotes('Here is the task dashboard running on OKE. You can see 3 active tasks with priority tags, due dates, and recurring task support. The AI chat assistant on the right can create tasks via natural language - I typed Add a task for tomorrow and it created one automatically.');

  // Slide 9: Cloud Highlights
  const s9 = await html2pptx(path.join(SLIDES_DIR, 'slide09-cloud-highlights.html'), pptx);
  s9.slide.addNotes('Key deployment highlights: zero cost on OCI free tier, single node cluster, 5 pods running including Kafka with Dapr sidecar on backend. The app runs 24/7. CPU usage is only 24% of budget and RAM is only 10% of the 8GB available.');

  // Slide 10: Event Flow
  const s10 = await html2pptx(path.join(SLIDES_DIR, 'slide10-event-flow.html'), pptx);
  s10.slide.addNotes('The event flow is: user creates a task, FastAPI backend processes it, Dapr sidecar publishes the event, and Kafka stores it in the todo-events topic. This is a fire-and-forget pattern so it does not slow down the API response. Kafka uses KRaft mode which eliminates the need for Zookeeper.');

  // Slide 11: Resource Table
  const s11 = await html2pptx(path.join(SLIDES_DIR, 'slide11-resources.html'), pptx);
  if (s11.placeholders.length > 0) {
    const p = s11.placeholders[0];
    s11.slide.addTable([
      [
        { text: 'Component', options: { fill: { color: '1C2833' }, color: 'FFFFFF', bold: true, fontSize: 12 } },
        { text: 'CPU Request', options: { fill: { color: '1C2833' }, color: 'FFFFFF', bold: true, fontSize: 12 } },
        { text: 'CPU Limit', options: { fill: { color: '1C2833' }, color: 'FFFFFF', bold: true, fontSize: 12 } },
        { text: 'RAM Request', options: { fill: { color: '1C2833' }, color: 'FFFFFF', bold: true, fontSize: 12 } },
        { text: 'RAM Limit', options: { fill: { color: '1C2833' }, color: 'FFFFFF', bold: true, fontSize: 12 } }
      ],
      ['Backend', '64m', '250m', '128Mi', '384Mi'],
      ['Frontend', '64m', '250m', '128Mi', '384Mi'],
      ['Kafka (KRaft)', '100m', '500m', '512Mi', '1Gi'],
      ['Dapr Sidecar', '10m', '100m', '32Mi', '64Mi'],
      ['NGINX Ingress', '50m', '200m', '64Mi', '128Mi'],
      [
        { text: 'TOTAL', options: { bold: true, color: 'E67E22' } },
        { text: '288m', options: { bold: true, color: 'E67E22' } },
        { text: '1300m', options: { bold: true, color: 'E67E22' } },
        { text: '864Mi', options: { bold: true, color: 'E67E22' } },
        { text: '2.0Gi', options: { bold: true, color: 'E67E22' } }
      ]
    ], {
      x: p.x, y: p.y, w: p.w,
      colW: [p.w * 0.28, p.w * 0.18, p.w * 0.18, p.w * 0.18, p.w * 0.18],
      border: { pt: 0.5, color: 'D5D8DC' },
      align: 'center',
      valign: 'middle',
      fontSize: 11,
      rowH: [0.4, 0.35, 0.35, 0.35, 0.35, 0.35, 0.4]
    });
  }
  s11.slide.addNotes('This table shows resource allocation for each component. Total CPU requests are 288m out of 1000m available (29%), and RAM requests are 864Mi out of 8GB (11%). We have plenty of headroom on the free-tier node.');

  // Slide 12: Verification
  const s12 = await html2pptx(path.join(SLIDES_DIR, 'slide12-verification.html'), pptx);
  s12.slide.addNotes('All 9 verification checks pass. Every pod is running, services have correct ports, ingress has the LoadBalancer IP assigned, both frontend and backend respond to HTTP requests, authentication works end-to-end, CRUD operations are verified, Dapr events publish to Kafka, and resource usage fits within budget. 33 out of 33 tasks completed.');

  // Slide 13: Future Work
  const s13 = await html2pptx(path.join(SLIDES_DIR, 'slide13-future.html'), pptx);
  s13.slide.addNotes('For future improvements: First, add HTTPS with cert-manager and Lets Encrypt. Second, buy a custom domain. Third, set up CI/CD with GitHub Actions. Fourth, add monitoring with Prometheus and Grafana. Fifth, implement Kafka consumers for notifications and analytics.');

  // Slide 14: Thank You with photo
  const s14 = await html2pptx(path.join(SLIDES_DIR, 'slide14-thankyou.html'), pptx);
  s14.slide.addImage({ path: PHOTO, x: 8.3, y: 3.2, w: 1.3, h: 1.3, rounding: true });
  s14.slide.addNotes('Thank you for your attention. The app is live at both URLs shown. I am happy to take any questions about the architecture, deployment process, or challenges we solved.');

  await pptx.writeFile({ fileName: path.join(ROOT, 'todo-app-oke-presentation.pptx') });
  console.log('Presentation created: todo-app-oke-presentation.pptx');
}

create().catch(e => { console.error(e); process.exit(1); });
