export const ACCESS_TOKEN = 'access';
export const REFRESH_TOKEN = 'refresh';

export const apiUrl = import.meta.env.VITE_API_URL;

//the one without /api/
export const backendOrigin = new URL(apiUrl).origin;

//getting the default image in ../backend/media/item_iamges
export const DEFAULT_IMAGE = `${backendOrigin}/media/item_images/default.png`;