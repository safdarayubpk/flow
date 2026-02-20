const sharp = require('sharp');

async function createAssets() {
  // Dark gradient for title/section slides
  const darkGrad = `<svg xmlns="http://www.w3.org/2000/svg" width="1920" height="1080">
    <defs><linearGradient id="g" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:#1C2833"/>
      <stop offset="100%" style="stop-color:#2E4053"/>
    </linearGradient></defs>
    <rect width="100%" height="100%" fill="url(#g)"/>
  </svg>`;
  await sharp(Buffer.from(darkGrad)).png().toFile('pptx-workspace/dark-bg.png');

  // Light gradient for content slides
  const lightGrad = `<svg xmlns="http://www.w3.org/2000/svg" width="1920" height="1080">
    <defs><linearGradient id="g" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" style="stop-color:#FFFFFF"/>
      <stop offset="100%" style="stop-color:#F4F6F6"/>
    </linearGradient></defs>
    <rect width="100%" height="100%" fill="url(#g)"/>
  </svg>`;
  await sharp(Buffer.from(lightGrad)).png().toFile('pptx-workspace/light-bg.png');

  // Orange accent bar
  const accentBar = `<svg xmlns="http://www.w3.org/2000/svg" width="1920" height="8">
    <rect width="100%" height="100%" fill="#E67E22"/>
  </svg>`;
  await sharp(Buffer.from(accentBar)).png().toFile('pptx-workspace/accent-bar.png');

  console.log('Assets created');
}
createAssets().catch(console.error);
