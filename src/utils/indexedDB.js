const IMAGE_CACHE_EXPIRATION_DAYS = 7;
const openDatabase = () => {
  return new Promise((resolve, reject) => {
    const request = indexedDB.open("ImageCacheDB", 1);
    request.onupgradeneeded = (event) => {
      const db = event.target.result;
      if (!db.objectStoreNames.contains("images")) {
        db.createObjectStore("images", { keyPath: "id" });
      }
    };
    request.onsuccess = () => resolve(request.result);
    request.onerror = () => reject(request.error);
  });
};

// Utility to get an image from IndexedDB
export const getCachedImage = async (cardId) => {
  const db = await openDatabase();
  return new Promise((resolve, reject) => {
    const transaction = db.transaction("images", "readonly");
    const store = transaction.objectStore("images");
    const request = store.get(cardId);
    request.onsuccess = () => {
      const result = request.result;
      if (result) {
        const now = Date.now();
        const cacheAge = (now - result.timestamp) / (1000 * 60 * 60 * 24); // Age in days
        if (cacheAge > IMAGE_CACHE_EXPIRATION_DAYS) {
          // Image has expired
          resolve(null);
        } else {
          // Return cached image
          resolve(result.image);
        }
      } else {
        resolve(null);
      }
    };
    request.onerror = () => reject(request.error);
  });
};

// Utility to cache an image in IndexedDB
export const cacheImageInDB = async (cardId, image) => {
  const db = await openDatabase();
  return new Promise((resolve, reject) => {
    const transaction = db.transaction("images", "readwrite");
    const store = transaction.objectStore("images");
    const request = store.put({ id: cardId, image, timestamp: Date.now() });
    request.onsuccess = () => resolve();
    request.onerror = () => reject(request.error);
  });
};

// Utility to clear expired images
export const clearExpiredImages = async () => {
  const db = await openDatabase();
  const transaction = db.transaction("images", "readwrite");
  const store = transaction.objectStore("images");
  const request = store.openCursor();
  request.onsuccess = (event) => {
    const cursor = event.target.result;
    if (cursor) {
      const cacheAge = (Date.now() - cursor.value.timestamp) / (1000 * 60 * 60 * 24);
      if (cacheAge > IMAGE_CACHE_EXPIRATION_DAYS) {
        store.delete(cursor.key);
      }
      cursor.continue();
    }
  };
};

