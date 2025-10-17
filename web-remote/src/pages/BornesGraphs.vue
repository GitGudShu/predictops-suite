<template>
  <q-page>
    <BackButton />
    <div class="container">
      <q-expansion-item v-for="(category, categoryName) in orderedDptBounds" :key="categoryName"
        :label="capitalize(categoryName)" class=" text-black"
        :header-style="{ fontSize: '20px', fontWeight: 'bold', padding: '15px' }">
        <p v-if="categoryName == 'Horloge des appels'" class="q-ma-md text-italic text-subtitle1">Le premier champ
          correspond au nombre d'appels sur une tranche de 3h. <br> Le deuxième correspond au nombre d'opérateurs.</p>
        <div v-for="(criteriaList, criteriaName) in category" :key="criteriaName" class="q-pa-md">
          <h6>{{ criteriaName }}</h6>
          <div v-for="(value, key) in orderedCriteria(criteriaList)" :key="key">
            <div class="q-mb-md flex">

              <span class="form-label text-bold" :class="`underline-${key}`">
                {{ capitalize(key) }} :
              </span>
              <div class="form-input flex">
                <span v-if="value.prefix" class="text-h6">{{ value.prefix }}</span>
                <q-input square v-model="value.value" filled dense style="width: 100px" />
              </div>
              <div v-if="'operators' in value" class="operators">
                <span>Opérateurs : </span>
                <span v-if="value.prefix" class="text-h6">{{ value.prefix }}</span>
                <q-input square v-model="value.operators" filled dense style="width: 100px" />
              </div>
              <div class="q-ml-sm text-bold">{{ value.unit }}</div>
            </div>
          </div>
          <q-separator></q-separator>
        </div>
      </q-expansion-item>
    </div>
    <Button @click="saveData" btn-text="Enregistrer" btn-size="lg-btn" left-icon="fa-solid fa-floppy-disk"
      left-icon-size="sm" bg-color="var(--sad-nightblue)" txt-color="white" style="margin: 1rem auto;">
    </Button>
  </q-page>
</template>

<script setup>
import { ref, computed } from 'vue'
import BackButton from 'src/components/BackButton.vue'
import Button from 'src/components/Button.vue';
import { api } from 'src/boot/axios'
import { notifyUser } from 'src/utils/notifyUser'
import { useRoute } from 'vue-router'

const location = useRoute();


const dpt = ref(localStorage.getItem("dpt") || location.params.dpt)
const dptBounds = ref(JSON.parse(localStorage.getItem("dptBounds") || '{}'))
const orderedKeys = ["Qualité des interventions", "Qualité des appels", "Graphique décrochés d'appels", "Horloge des appels"]
const orderedDptBounds = computed(() => {
  let orderedObject = {};

  orderedKeys.forEach(key => {
    if (dptBounds.value[key]) {
      orderedObject[key] = dptBounds.value[key];
    }
  });

  // Then, add the rest of the keys in their original order
  Object.keys(dptBounds.value).forEach(key => {
    if (!orderedKeys.includes(key)) {
      orderedObject[key] = dptBounds.value[key];
    }
  });

  return orderedObject;
});
const capitalize = (str) => str.charAt(0).toUpperCase() + str.slice(1);

const colorOrder = ['vert', 'jaune', 'orange', 'rouge'];

const orderedCriteria = (criteriaList) => {
  const ordered = {};
  // Ensure specified color order for known colors
  colorOrder.forEach(color => {
    if (criteriaList[color]) {
      ordered[color] = criteriaList[color];
    }
  });
  // Add remaining criteria not included in colorOrder
  Object.keys(criteriaList).forEach(key => {
    if (!ordered[key]) {
      ordered[key] = criteriaList[key];
    }
  });
  return ordered;
};


const saveData = async () => {
  try {
    const data = { ...orderedDptBounds.value, "dpt": dpt.value }
    await api.put("admin/update/bounds", data);
    localStorage.setItem("dptBounds", JSON.stringify(orderedDptBounds.value))
    notifyUser({ icon: "check", message: "Enregistrement avec succès.", color: "green", position: "bottom", timeout: 2500 })
  } catch (e) {
    notifyUser({ icon: "error", message: "Erreur lors de la sauvegarde.", color: "red", position: "bottom", timeout: 2500 })
  }

};

</script>

<style scoped>

.container {
  width: 80%;
  margin: 1em auto;
  background: white;
  box-shadow: 0px 3px 24px 0px var(--sad-lightgray);

}

h6 {
  margin: 0 0 1em 0;
}

.form-label {
  min-width: 50px;
  position: relative;
}

.form-input {
  flex: 0;
}

.form-input label {
  flex: 1;
}

.form-input span {
  flex: 0;
}

.flex {
  display: flex;
  align-items: center;
  gap: 1em;
}

.operators {
  display: flex;
  align-items: center;
  gap: 1em;
  font-weight: bold;
}

.form-label::before {
  height: 5px;
  content: "";
  position: absolute;
  width: 100%;
  top: 100%;
}

.underline-vert::before {
  background-color: var(--sad-green);
}

.underline-jaune::before {
  background-color: var(--sad-yellow);
}

.underline-orange::before {
  background-color: var(--sad-orange);
}

.underline-rouge::before {
  background-color: var(--sad-red);
}

.underline-violet::before {
  background-color: var(--sad-purple);
}
</style>
