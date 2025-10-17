<template>
  <q-page>
    <div class="wrapper">
      <div class="container">
        <div class="header">
          <q-icon name="manage_accounts" size="lg"></q-icon>
          <h3>Mon compte</h3>
          <q-separator size="3px"/>
        </div>
        <div class="cta-cards-container">
          <CTACard path="parametres/update-password" icon="lock" title="Mot de passe" arrowIcon="trending_flat">
            <template #body>Modifier le mot de passe.</template>
          </CTACard>
        </div>
      </div>
      <div class="container" v-if="admin">
        <div class="header">
          <q-icon name="mdi-security" size="lg"></q-icon>
          <h3>Administration</h3>
          <q-separator size="3px"/>
        </div>
        <div class="cta-cards-container">
          <CTACard path="parametres/users" icon="fa-solid fa-users" title="Utilisateurs" arrowIcon="trending_flat">
            <template #body>Gérer les utilisateurs, leurs accès...</template>
          </CTACard>
          <CTACard path="parametres/pages" icon="fa-solid fa-window-restore" title="Pages" arrowIcon="trending_flat">
            <template #body>Gérer les pages et sous-pages.</template>
          </CTACard>
          <CTACard path="parametres/popups" icon="campaign" title="Alertes" arrowIcon="trending_flat" v-show="decodedUser.role === 'maintainer'">
            <template #body>
              Créer, supprimer ou modifier des alertes.
            </template>
          </CTACard>
          <CTACard path="parametres/listes-de-diffusion" icon="fa-solid fa-envelopes" title="Listes de diffusion" arrowIcon="trending_flat">
            <template #body>
              Gérer les listes de diffusion.
            </template>
          </CTACard>
          <CTACard path="parametres/sante" icon="fa-solid fa-laptop-medical" title="Santé" arrowIcon="trending_flat" v-show="decodedUser.role === 'maintainer'">
            <template #body>
              Vérifier l'état de la donnée et du flux.
            </template>
          </CTACard>
        </div>
      </div>
      <div class="container" v-if="admin">
        <div class="header">
          <q-icon name="tune" size="lg"></q-icon>
          <h3>Bornes des graphiques et des cartes</h3>
          <q-separator size="3px"/>
        </div>
        <div class="cta-cards-container">
          <CTACard path="parametres/bornes-graphiques" icon="ssid_chart" title="Graphiques" arrowIcon="trending_flat">
            <template #body>Modifier les bornes des graphiques.</template>
          </CTACard>
          <CTACard path="parametres/bornes-cartes" icon="mdi-map" title="Cartes" arrowIcon="trending_flat">
            <template #body>
              Modifier les bornes des cartes par centre, par CIS, par type d'intervention...
            </template>
          </CTACard>
        </div>
      </div>
    </div>

  </q-page>
</template>

<script setup>
import { ref } from "vue";
import CTACard from 'src/components/CTACard.vue';
import { Base64 } from 'js-base64'
import { Cookies } from 'quasar'


const decodedUser = JSON.parse(Base64.decode(Cookies.get('user')))

const admin = ref(decodedUser.role === 'admin' || decodedUser.role === 'maintainer')

</script>

<style scoped>
.wrapper {
  display: flex;
  justify-content: center;
  flex-direction: column;
  gap: 1em;
  width: 70%;
  margin: 0 auto;
  height: 100%;
}
.container {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
}

.container .header {
  display: flex;
  align-items: center;
  gap: 1em;
  padding: 0 2em;
  color: var(--sad-nightblue);
}
.container .header h3 {
  margin: 5px;
  font-size: clamp(1.5em, 3vw, 2em);
  font-weight: 500;
}
.q-separator {
  flex: 1;
  background: var(--sad-nightblue);
}
.cta-cards-container {
  width: 100%;
  min-height: 100%;
  display: flex;
  justify-content: space-evenly;
  align-items: center;
  padding: 2em;
  flex-wrap: wrap;
  gap: 1.5em;
}

@media screen and (max-width: 1200px) {
  .wrapper {
    width: 80%;
  }
}
@media screen and (max-width: 750px) {
  .wrapper {
    width: 100%;
  }
}
</style>
