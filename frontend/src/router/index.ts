import { createRouter, createWebHistory } from "vue-router";

const LoginView = () => import("../views/LoginView.vue");
const AdminHomeView = () => import("../views/admin/AdminHomeView.vue");
const EventConfigView = () => import("../views/admin/EventConfigView.vue");
const DepartView = () => import("../views/admin/DepartView.vue");
const SuiviView = () => import("../views/admin/SuiviView.vue");
const ResultatsView = () => import("../views/admin/ResultatsView.vue");
const TemplateConfigView = () => import("../views/admin/TemplateConfigView.vue");
const PublicResultsView = () => import("../views/public/PublicResultsView.vue");
const PublicBeaconEditView = () => import("../views/public/PublicBeaconEditView.vue");
const PublicEventsListView = () => import("../views/public/PublicEventsListView.vue");
const PublicSplitTimesView = () => import("../views/public/PublicSplitTimesView.vue");

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: "/",
      name: "root",
      redirect: () => {
        const token = localStorage.getItem("token");
        if (token) {
          try {
            const payload = JSON.parse(atob(token.split(".")[1]));
            if (payload.exp && Date.now() < payload.exp * 1000 && payload.role === "organizer") {
              return "/admin";
            }
          } catch { /* invalid token */ }
        }
        return "/login";
      },
    },
    {
      path: "/login",
      name: "login",
      component: LoginView,
    },
    {
      path: "/admin",
      name: "admin-home",
      component: AdminHomeView,
      meta: { requiresAuth: true },
    },
    {
      path: "/admin/templates/:id",
      name: "template-config",
      component: TemplateConfigView,
      meta: { requiresAuth: true },
    },
    {
      path: "/admin/events/:id/config",
      name: "event-config",
      component: EventConfigView,
      meta: { requiresAuth: true },
    },
    {
      path: "/admin/events/:id/depart",
      name: "event-depart",
      component: DepartView,
      meta: { requiresAuth: true },
    },
    {
      path: "/admin/events/:id/suivi",
      name: "event-suivi",
      component: SuiviView,
      meta: { requiresAuth: true },
    },
    {
      path: "/admin/events/:id/resultats",
      name: "event-resultats",
      component: ResultatsView,
      meta: { requiresAuth: true },
    },
    {
      path: "/events",
      name: "public-events-list",
      component: PublicEventsListView,
    },
    {
      path: "/events/:id",
      name: "public-results",
      component: PublicResultsView,
    },
    {
      path: "/events/:id/splits",
      name: "public-splits",
      component: PublicSplitTimesView,
    },
    {
      path: "/events/:id/competitor/:userId/beacons",
      name: "public-beacon-edit",
      component: PublicBeaconEditView,
    },
  ],
});

function getUserRole(): string | null {
  const token = localStorage.getItem("token");
  if (!token) return null;
  try {
    const payload = JSON.parse(atob(token.split(".")[1]));
    if (payload.exp && Date.now() >= payload.exp * 1000) {
      localStorage.removeItem("token");
      return null;
    }
    return payload.role ?? null;
  } catch {
    return null;
  }
}

router.beforeEach((to) => {
  const role = getUserRole();
  if (to.meta.requiresAuth && role !== "organizer") {
    return { name: "login" };
  }
  if (to.name === "login" && role === "organizer") {
    return { name: "admin-home" };
  }
});

export default router;

