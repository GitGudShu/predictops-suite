import { route } from "quasar/wrappers";
import {
  createRouter,
  createMemoryHistory,
  createWebHistory,
  createWebHashHistory,
} from "vue-router";
import routes from "./routes";
import { api } from "src/boot/axios";
import { showDialog } from "src/utils/dialogUtil";
import { Cookies } from "quasar";

export default route(function () {
  const createHistory = process.env.SERVER
    ? createMemoryHistory
    : process.env.VUE_ROUTER_MODE === "history"
    ? createWebHistory
    : createWebHashHistory;

  const Router = createRouter({
    scrollBehavior: () => ({ left: 0, top: 0 }),
    routes,
    history: createHistory(process.env.VUE_ROUTER_BASE),
  });

  let isSkippingAuthCheck = false;
  let isAuthError = false;
  let wasAuthenticated = false; // Track if the user had a valid session

  Router.beforeEach(async (to, from, next) => {
    const hasUserCookie = Cookies.has("user");
    const isLoginPage = to.path === "/login";
    const isPublicPage =
      to.path.includes(process.env.UUID) ||
      to.path === "/password/reset" ||
      to.path === "/password/forgotten";

    if (!hasUserCookie && !isPublicPage && !isLoginPage) {
      return next("/login");
    }

    // If on login page without cookie, just go through, no loop.
    if (isLoginPage && !hasUserCookie) {
      return next();
    }

    // If on login page and user cookie exists, redirect to home or previous page
    if (isLoginPage && hasUserCookie) {
      return next(from.fullPath && from.fullPath !== "/login" ? from.fullPath : "/");
    }

    // Public page: skip checks
    if (isPublicPage) {
      return next();
    }

    // If skipping auth check once (e.g., after a redirect), proceed
    if (isSkippingAuthCheck) {
      isSkippingAuthCheck = false;
      return next();
    }

    // For protected routes:
    if (hasUserCookie) {
      try {
        const response = await api.post("/auth/check-auth");
        const isAuthenticated = response.data.isAuthenticated;

        if (isAuthenticated) {
          wasAuthenticated = true; // Now we know user had a valid session
          return next();
        } else {
          // Not authenticated anymore, remove cookie and redirect
          Cookies.remove("user");
          isSkippingAuthCheck = true;
          return next("/login");
        }
      } catch (error) {
        // Server check failed, assume not authenticated
        Cookies.remove("user");
        isSkippingAuthCheck = true;
        return next("/login");
      }
    }

    // If none of the above apply, proceed
    return next();
  });

  Router.afterEach(async (to, from) => {
    const colorMap = {
      info: "#74c0fc",
      warning: "#fed330",
      error: "#c92a2a",
    };
    const dpt = window.localStorage.getItem("dpt");
    if (
      dpt &&
      to.path !== "/login" &&
      !to.path.includes(process.env.UUID) &&
      to.path !== "/password/reset" &&
      to.path !== "/password/forgotten"
    ) {
      await api.get(`/data/popup?dpt=${dpt}`).then((res) => {
        if (res.status == 200) {
          const popup = res.data;
          if (!hasPopupBeenSeen(popup._id) && popup.visible) {
            showDialog(
              {
                focus: "none",
                style: {
                  width: "50%",
                  maxWidth: "unset !important",
                  backgroundColor: colorMap[popup.type],
                  color: "black",
                },
                html: true,
                message: popup.message,
                ok: {
                  label: "OK",
                  color: "primary",
                  align: "center",
                },
              },
              () => markPopupAsSeen(popup._id),
              () => markPopupAsSeen(popup._id)
            );
          }
        }
      });
    }
  });

  function hasPopupBeenSeen(popupId) {
    const seenPopups = JSON.parse(localStorage.getItem("seenPopups") || "[]");
    return seenPopups.includes(popupId);
  }

  function markPopupAsSeen(popupId) {
    const seenPopups = JSON.parse(localStorage.getItem("seenPopups") || "[]");
    seenPopups.push(popupId);
    localStorage.setItem("seenPopups", JSON.stringify(seenPopups));
  }

  api.interceptors.response.use(
    (response) => {
      return response;
    },
    async (error) => {
      if (error.response && error.response.status === 401) {
        // Remove the user cookie so route guards redirect to login naturally
        Cookies.remove("user");

        if (!isAuthError && wasAuthenticated) {
          isAuthError = true;
          isSkippingAuthCheck = true;
          // First, navigate to login
          await Router.replace("/login");
          // After navigation completes, show the disconnected dialog
          setTimeout(() => {
            showDialog(
              {
                focus: "none",
                style: {
                  minWidth: "300px !important",
                  backgroundColor: "#181632",
                  color: "white",
                },
                html: true,
                message: "Vous avez été déconnecté(e).",
                ok: {
                  label: "OK",
                  color: "secondary",
                  align: "center",
                },
              },
              () => {
                isAuthError = false;
              },
              () => {
                isAuthError = false;
              }
            );
          }, 0);
        } else {
          // If never authenticated or already handled error, just ensure redirection
          isSkippingAuthCheck = true;
          await Router.replace("/login");
        }
      }
      return Promise.reject(error);
    }
  );

  api.interceptors.request.use(
    (config) => {
      if (isAuthError) {
        return Promise.reject({
          message: "Session expired, preventing further API calls.",
        });
      }
      return config;
    },
    (error) => {
      return Promise.reject(error);
    }
  );

  return Router;
});
