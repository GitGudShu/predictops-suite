import { nextTick } from 'vue';

export const adjustFontSize = async (element, minFontSize = 10, step = 1, grow = false) => {
  await nextTick();  // Ensure the DOM updates are completed before checking sizes

  let currentFontSize = parseFloat(getComputedStyle(element).fontSize);
  let originalFontSize = currentFontSize;
  let maxFontSize = 100; // Arbitrary large number for max font size

  const adjustDown = () => {
    // Decrease font size until it fits within the element's bounds
    while ((element.scrollWidth > element.offsetWidth || element.scrollHeight > element.offsetHeight) && currentFontSize > minFontSize) {
      currentFontSize -= step;  // Decrease font size in steps
      element.style.fontSize = `${currentFontSize}px`;  // Apply the new font size
    }
  };

  const adjustUp = () => {
    // Increase font size until it causes overflow
    while ((element.scrollWidth <= element.offsetWidth && element.scrollHeight <= element.offsetHeight) && currentFontSize < maxFontSize) {
      currentFontSize += step;  // Increase font size in steps
      element.style.fontSize = `${currentFontSize}px`;  // Apply the new font size
    }

    adjustDown()
  };

  if (grow) {
    adjustUp();
  } else {
    adjustDown();
  }
};

const luminance = (r, g, b) => {
  const a = [r, g, b].map(v => {
    v /= 255;
    return v <= 0.03928 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4);
  });
  return a[0] * 0.2126 + a[1] * 0.7152 + a[2] * 0.0722;
};

const contrastRatio = (lum1, lum2) => {
  return (Math.max(lum1, lum2) + 0.05) / (Math.min(lum1, lum2) + 0.05);
};

const hexToRgb = (hex) => {
  let bigint = parseInt(hex.slice(1), 16);
  let r = (bigint >> 16) & 255;
  let g = (bigint >> 8) & 255;
  let b = bigint & 255;
  return [r, g, b];
};

export const determineTextColor = (bgColor) => {
  const [r, g, b] = hexToRgb(bgColor);
  const bgLum = luminance(r, g, b);
  const whiteLum = luminance(255, 255, 255);
  const darkLum = luminance(24, 22, 50); // Adjust this RGB value for var(--sad-nightblue)

  const contrastWithWhite = contrastRatio(bgLum, whiteLum);
  const contrastWithDark = contrastRatio(bgLum, darkLum);

  return contrastWithWhite > contrastWithDark ? '#FFFFFF' : 'var(--sad-nightblue)';
};
