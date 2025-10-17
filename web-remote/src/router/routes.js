import MainLayout from "layouts/MainLayout.vue";
import LoginLayout from "layouts/LoginLayout.vue";
import PermanencesLayout from "layouts/PermanencesLayout.vue";
import PasswordLayout from "layouts/PasswordLayout.vue";
import SlideshowLayout from "layouts/SlideshowLayout.vue";
import Parametres from "pages/Parametres.vue";
import Synthese from "pages/Synthese.vue";
import Appels from "pages/Appels.vue";
import VariableExplicatives from "pages/VariableExplicatives.vue";
import Fiabilite from "pages/Fiabilite.vue";
import PrevisionsSemaine from "pages/PrevisionsSemaine.vue";
import Incendies from "pages/Incendies.vue";
import Login from "pages/Login.vue";
import Meteo from "pages/Meteo.vue";
import Inondations from "pages/Inondations.vue";
import SAP from "pages/SAP.vue";
import ChaineDeCommandement from "pages/ChaineDeCommandement.vue";
import Astreintes from "pages/Astreintes.vue";
import Specialistes from "pages/Specialistes.vue";
import ResetPassword from "pages/ResetPassword.vue";
import ForgottenPassword from "pages/ForgottenPassword.vue";
import BornesGraphs from "pages/BornesGraphs.vue";
import BornesCartes from "pages/BornesCartes.vue";
import UpdatePassword from "pages/UpdatePassword.vue";
import Users from "pages/Users.vue";
import Popups from "pages/Popups.vue";
import Health from "pages/Health.vue"
import Pages from "src/pages/Pages.vue";
import ListesDiffusion from "src/pages/ListesDiffusion.vue";
import SalleCTA from "src/pages/SalleCTA.vue";
import Consignes from "src/pages/Consignes.vue";
import Historique from "src/pages/Historique.vue";

const routes = [
  {
    path: "/",
    component: MainLayout,
    children: [
      {
        path: "",
        component: Synthese,
        redirect: "synthese",
      },
      {
        path: "synthese",
        component: Synthese,
      },
      {
        path: "appels",
        component: Appels,
      },
      {
        path: "variables-explicatives",
        component: VariableExplicatives,
      },
      {
        path: "fiabilite",
        component: Fiabilite,
      },
      {
        path: "previsions-semaine",
        component: PrevisionsSemaine,
      },
      {
        path: "feux-espaces-naturels",
        component: Incendies,
      },
      {
        path: "meteo",
        component: Meteo,
      },
      {
        path: "inondations",
        component: Inondations,
      },
      {
        path: "sap-total",
        component: SAP,
      },
      {
        path: "historique",
        component: Historique,
      },
      {
        path: "consignes",
        component: Consignes,
      },
    ],
  },
  {
    path: "/permanences",
    component: PermanencesLayout,
    children: [
      {
        path: "",
        redirect: "/permanences/chaine-de-commandement",
      },
      {
        path: "chaine-de-commandement",
        component: ChaineDeCommandement,
      },
      {
        path: "astreintes",
        component: Astreintes,
      },
      {
        path: "specialistes",
        component: Specialistes,
      },
    ],
  },
  {
    path: "/parametres",
    component: MainLayout,
    children: [
      {
        path: "",
        component: Parametres,
      },
      {
        path: "bornes-graphiques",
        component: BornesGraphs,
      },
      {
        path: "bornes-cartes",
        component: BornesCartes,
      },
      {
        path: "update-password",
        component: UpdatePassword,
      },
      {
        path: "users",
        component: Users,
      },
      {
        path: "popups",
        component: Popups,
      },
      {
        path: "sante",
        component: Health,
      },
      {
        path: "pages",
        component: Pages,
      },
      {
        path: "listes-de-diffusion",
        component: ListesDiffusion,
      },
    ],
  },
  {
    path: "/login",
    component: LoginLayout,
    children: [
      {
        path: "",
        component: Login,
      },
    ],
  },
  {
    path: `/:dpt/${process.env.UUID}/:page`,
    component: SlideshowLayout,
    children: [
      {
        path: "",
        component: SalleCTA,
      },
    ],
  },
  {
    path: "/mot-de-passe",
    component: PasswordLayout,
    children: [
      {
        path: "reset",
        component: ResetPassword,
      },
      {
        path: "forgotten",
        component: ForgottenPassword,
      },
    ],
  },

  {
    path: "/:catchAll(.*)*",
    component: () => import("pages/ErrorNotFound.vue"),
  },
];

export default routes;
