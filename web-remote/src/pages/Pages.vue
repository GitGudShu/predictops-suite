<template>
  <q-page>
    <div class="actions-bar">
      <BackButton />
    </div>
    <div class="container">
      <!-- Draggable pages -->
      <VueDraggable v-model="pagesList" item-key="dpt" class="draggable-list" :disabled="true">
        <template v-for="pages in pagesList" :key="pages.dpt">
          <q-expansion-item :label="'Département du ' + pages.dpt" class="page-expansion-item">
            <!-- Draggable page items -->
            <VueDraggable v-model="pages.pages" @end="reorderPages(pages.dpt)" item-key="path" handle=".page-handle"
              class="draggable-pages">
              <template v-for="page in pages.pages" :key="page.path">
                <div class="page-item">
                  <q-icon v-if="page.disabled" name="fa-solid fa-bars" class="page-handle" size="16px"></q-icon>
                  <q-expansion-item v-if="page.subpages" :label="page.name" :icon="page.icon"
                    class="subpage-expansion-item">
                    <!-- Draggable subpage items -->
                    <VueDraggable v-model="page.subpages" @end="reorderSubpages(pages.dpt, page.path)" item-key="path"
                      handle=".subpage-handle" class="draggable-subpages">
                      <template v-for="subpage in page.subpages" :key="subpage.path">
                        <div class="subpage-item">
                          <q-icon name="fa-solid fa-bars" class="subpage-handle" size="16px"></q-icon>
                          <q-icon :name="subpage.icon" class="subpage-icon" size="sm"></q-icon>
                          <div class="subpage-name">{{ subpage.name }}
                            <router-link :to="'/' + subpage.path" target="_blank">({{ subpage.path }}
                              <q-icon name="fa-solid fa-external-link" size="10px" />
                            </router-link>)
                          </div>
                          <div class="subpage-actions">
                            <Button left-icon="fa-solid fa-pen" @click="editSubpage(pages.dpt, subpage)"
                              bg-color="transparent" txt-color="var(--sad-nightblue)" />
                            <q-separator vertical inset />
                            <Button left-icon="mdi-delete-empty" @click="deleteSubpage(pages.dpt, page, subpage)"
                              bg-color="transparent" txt-color="var(--sad-red)" />
                          </div>
                          <!-- Edit subpage form -->
                          <q-form
                            v-if="editingSubpage && subpage.path === subpageEdit.path && pages.dpt === editingSubpageDpt"
                            @submit="confirmEditSubpage(pages.dpt, page)" @reset="discardEditSubpage"
                            class="edit-subpage-form">
                            <q-icon :name="subpageEdit.icon" class="edit-subpage-icon" size="sm"></q-icon>
                            <q-input v-model="subpageEdit.icon" label="Icône" bg-color="white" type="text" outlined
                              dense :rules="[val => val && val.length > 0 && val !== '' || 'Champ obligatoire']"
                              hide-bottom-space />
                            <q-input v-model="subpageEdit.name" label="Nom" bg-color="white" type="text" outlined dense
                              :rules="[val => val && val.length > 0 && val !== '' || 'Champ obligatoire']"
                              hide-bottom-space />
                            <div class="edit-subpage-actions">
                              <Button left-icon="mdi-close" bg-color="transparent" btn-type="reset"
                                txt-color="var(--sad-red)" />
                              <q-separator vertical inset />
                              <Button left-icon="mdi-check" bg-color="transparent" btn-type="submit"
                                txt-color="var(--sad-nightblue)" />
                            </div>
                          </q-form>
                        </div>
                      </template>
                    </VueDraggable>
                    <!-- Add new subpage form, buttons, etc. -->
                    <q-form v-if="addingSubpage && pages.dpt === addingSubpageDpt" class="new-subpage-form"
                      @submit="addNewSubpage(pages.dpt, page)" @reset="discardNewSubpage">
                      <q-icon :name="newSubpageIcon" class="new-subpage-icon" size="sm"></q-icon>
                      <q-input v-model="newSubpageIcon" label="Icône" bg-color="white" type="text" outlined dense
                        :rules="[val => val && val.length > 0 && val !== '' || 'Champ obligatoire']"
                        hide-bottom-space />
                      <q-input v-model="newSubpageName" label="Nom" bg-color="white" type="text" outlined dense
                        :rules="[val => val && val.length > 0 && val !== '' || 'Champ obligatoire']"
                        hide-bottom-space />
                      <q-input v-model="newSubpagePath" label="Chemin" bg-color="white" type="text" outlined dense
                        :rules="[val => val && val.length > 0 && val !== '' || 'Champ obligatoire']"
                        hide-bottom-space />
                      <div class="new-subpage-actions">
                        <Button left-icon="mdi-close" bg-color="transparent" btn-type="reset"
                          txt-color="var(--sad-red)" />
                        <q-separator vertical inset />
                        <Button left-icon="mdi-check" bg-color="transparent" btn-type="submit"
                          txt-color="var(--sad-nightblue)" />
                      </div>
                    </q-form>
                    <Button v-if="!addingSubpage && !editingSubpage && decodedUser.role === 'maintainer'" left-icon="mdi-plus"
                      @click="showAddSubpageForm(pages.dpt)" bg-color="transparent" txt-color="var(--sad-nightblue)"
                      left-icon-size="md" />
                  </q-expansion-item>

                  <!-- Page handle, name, and actions -->
                  <q-icon v-if="!page.disabled" name="fa-solid fa-bars" class="page-handle" size="16px"></q-icon>
                  <q-icon v-if="!page.disabled" :name="page.icon" class="page-icon" size="sm"></q-icon>
                  <div v-if="!page.disabled" class="page-name">{{ page.name }}
                    <router-link :to="'/' + page.path" target="_blank">({{ page.path }} <q-icon
                        name="fa-solid fa-external-link" size="10px" />)
                    </router-link>
                  </div>
                  <div v-if="!page.disabled" class="page-actions">
                    <Button left-icon="fa-solid fa-pen" @click="editPage(pages.dpt, page)" bg-color="transparent"
                      txt-color="var(--sad-nightblue)" />
                    <q-separator vertical inset />
                    <Button left-icon="mdi-delete-empty" @click="deletePage(pages.dpt, page)" bg-color="transparent"
                      txt-color="var(--sad-red)" />
                  </div>

                  <!-- Edit page form -->
                  <q-form v-if="editingPage && page.path === pageEdit.path && pages.dpt === editingPageDpt"
                    @submit="confirmEditPage(pages.dpt, page)" @reset="discardEditPage" class="edit-page-form">
                    <q-icon :name="pageEdit.icon" class="edit-page-icon" size="sm"></q-icon>
                    <q-input v-model="pageEdit.icon" label="Icône" bg-color="white" type="text" outlined dense
                      :rules="[val => val && val.length > 0 && val !== '' || 'Champ obligatoire']" hide-bottom-space />
                    <q-input v-model="pageEdit.name" label="Nom" bg-color="white" type="text" outlined dense
                      :rules="[val => val && val.length > 0 && val !== '' || 'Champ obligatoire']" hide-bottom-space />
                    <div class="edit-page-actions">
                      <Button left-icon="mdi-close" bg-color="transparent" btn-type="reset"
                        txt-color="var(--sad-red)" />
                      <q-separator vertical inset />
                      <Button left-icon="mdi-check" bg-color="transparent" btn-type="submit"
                        txt-color="var(--sad-nightblue)" />
                    </div>
                  </q-form>
                </div>
              </template>
            </VueDraggable>
            <!-- Add new page form, buttons, etc. -->
            <q-form v-if="addingPage && pages.dpt === addingPageDpt" class="new-page-form"
              @submit="addNewPage(pages.dpt, page)" @reset="discardNewPage">
              <q-icon :name="newPageIcon" class="new-page-icon" size="sm"></q-icon>
              <q-input v-model="newPageIcon" label="Icône" bg-color="white" type="text" outlined dense
                :rules="[val => val && val.length > 0 && val !== '' || 'Champ obligatoire']" hide-bottom-space />
              <q-input v-model="newPageName" label="Nom" bg-color="white" type="text" outlined dense
                :rules="[val => val && val.length > 0 && val !== '' || 'Champ obligatoire']" hide-bottom-space />
              <q-input v-model="newPagePath" label="Chemin" bg-color="white" type="text" outlined dense
                :rules="[val => val && val.length > 0 && val !== '' || 'Champ obligatoire']" hide-bottom-space />
              <div class="new-page-actions">
                <Button left-icon="mdi-close" bg-color="transparent" btn-type="reset" txt-color="var(--sad-red)" />
                <q-separator vertical inset />
                <Button left-icon="mdi-check" bg-color="transparent" btn-type="submit"
                  txt-color="var(--sad-nightblue)" />
              </div>
            </q-form>
            <Button v-if="!addingPage && !editingPage && decodedUser.role === 'maintainer'" left-icon="mdi-plus" @click="showAddPageForm(pages.dpt)"
              bg-color="transparent" txt-color="var(--sad-nightblue)" left-icon-size="md" />
          </q-expansion-item>
        </template>
      </VueDraggable>
    </div>
  </q-page>
</template>

<script setup>
import Button from "src/components/Button.vue";
import BackButton from "src/components/BackButton.vue";
import { ref, onMounted, inject } from "vue";
import { api } from "src/boot/axios";
import { notifyUser } from 'src/utils/notifyUser';
import { showDialog } from "src/utils/dialogUtil";
import { Base64 } from 'js-base64'
import { Cookies } from 'quasar'
import { VueDraggable } from 'vue-draggable-plus'

const getPages = inject('getPages')

const decodedUser = JSON.parse(Base64.decode(Cookies.get('user')))


const loading = ref()
const addingSubpage = ref(false)
const addingSubpageDpt = ref('')
const addingPage = ref(false)
const addingPageDpt = ref('')
const editingPage = ref(false)
const editingPageDpt = ref('')
const editingSubpage = ref(false)
const editingSubpageDpt = ref('')
const pageEdit = ref({})
const subpageEdit = ref({})

const pagesList = ref([])

const newSubpageIcon = ref('')
const newSubpageName = ref('')
const newSubpagePath = ref('')

const newPageIcon = ref('')
const newPageName = ref('')
const newPagePath = ref('')

const showAddPageForm = (dpt) => {
  addingPage.value = true
  addingPageDpt.value = dpt;
};

const addNewPage = async (dpt, page) => {
  try {
    const response = await api.post('/admin/add-page', {
      dpt: dpt,
      icon: newPageIcon.value,
      name: newPageName.value,
      path: newPagePath.value,
    })
    if (response.status === 200) {
      pagesList.value.find(p => p.dpt === dpt).pages.push({ icon: newPageIcon.value, name: newPageName.value, path: newPagePath.value })
      discardNewPage()
      getPages()
    }
    else {
      notifyUser({ icon: "error", message: response.data.error, color: "red", position: "bottom", timeout: 2500 })
    }
  }
  catch (error) {
    notifyUser({ icon: "error", message: error.response.data.error, color: "red", position: "bottom", timeout: 2500 })
  }
}

const discardNewPage = () => {
  addingPage.value = false
  newPageIcon.value = ''
  newPageName.value = ''
  newPagePath.value = ''
}

const editPage = (dpt, page) => {
  editingPageDpt.value = dpt
  editingPage.value = true
  pageEdit.value = JSON.parse(JSON.stringify(page));
}

const confirmEditPage = async (dpt, page) => {
  try {
    const response = await api.post(`/admin/edit-page`, {
      dpt: dpt,
      icon: pageEdit.value.icon,
      name: pageEdit.value.name,
      path: pageEdit.value.path
    })
    if (response.status === 200) {
      const pages = pagesList.value.find(pages => pages.dpt === dpt);
      const pageToUpdate = pages.pages.find(page => page.path === pageEdit.value.path);

      if (pageToUpdate) {
        pageToUpdate.icon = pageEdit.value.icon;
        pageToUpdate.name = pageEdit.value.name;
        pageToUpdate.path = pageEdit.value.path;
      }
      editingPage.value = false
      pageEdit.value = {}
      discardEditPage()
      getPages()
    }
  }
  catch (error) {
    notifyUser({ icon: "error", message: error.response.data.error, color: "red", position: "bottom", timeout: 2500 })
  }
}

const discardEditPage = () => {
  editingPageDpt.value = ''
  editingPage.value = false
  pageEdit.value = {}
}

const deletePage = async (dpt, page) => {
  try {
    const response = await api.delete('/admin/delete-page', {
      data: {
        dpt: dpt,
        path: page.path
      }
    })
    if (response.status === 200) {
      pagesList.value.find(p => p.dpt === dpt).pages = pagesList.value.find(p => p.dpt === dpt).pages.filter(p => p.path !== page.path)
      getPages()
    }
    else {
      notifyUser({ icon: "error", message: response.data.error, color: "red", position: "bottom", timeout: 2500 })
    }
  }
  catch (error) {
    notifyUser({ icon: "error", message: error.response.data.error, color: "red", position: "bottom", timeout: 2500 })
  }
}

const reorderPages = async (dpt) => {
  try {
    const response = await api.post('/admin/reorder-pages', {
      dpt: dpt,
      pages: pagesList.value.find(pages => pages.dpt === dpt)['pages']
    });
    if (response.status === 200) {
      notifyUser({ icon: "check", message: "Pages reorganisées.", color: "green", position: "bottom", timeout: 2500 })
      getPages()
    }
    else {
      notifyUser({ icon: "error", message: response.data.error, color: "red", position: "bottom", timeout: 2500 })
    }
  }
  catch (error) {
    notifyUser({ icon: "error", message: error.response.data.error, color: "red", position: "bottom", timeout: 2500 })
  }
}

const showAddSubpageForm = (dpt) => {
  addingSubpage.value = true
  addingSubpageDpt.value = dpt;
};
const addNewSubpage = async (dpt, page) => {
  try {
    const response = await api.post('/admin/add-subpage', {
      dpt: dpt,
      path: page.path,
      icon: newSubpageIcon.value,
      name: newSubpageName.value,
      subpage: newSubpagePath.value
    })
    if (response.status === 200) {
      page.subpages.push({ icon: newSubpageIcon.value, name: newSubpageName.value, path: newSubpagePath.value })
      discardNewSubpage()
      getPages()
    }
    else {
      notifyUser({ icon: "error", message: response.data.error, color: "red", position: "bottom", timeout: 2500 })
    }
  }
  catch (error) {
    notifyUser({ icon: "error", message: error.response.data.error, color: "red", position: "bottom", timeout: 2500 })
  }
}

const discardNewSubpage = () => {
  addingSubpage.value = false
  addingSubpageDpt.value = '';
  newSubpageIcon.value = ''
  newSubpageName.value = ''
  newSubpagePath.value = ''
}

const editSubpage = (dpt, subpage) => {
  editingSubpageDpt.value = dpt
  editingSubpage.value = true;
  subpageEdit.value = JSON.parse(JSON.stringify(subpage));
};

// Confirm and send the edited subpage to the server
const confirmEditSubpage = async (page) => {
  try {
    const response = await api.post(`/admin/edit-subpage`, {
      dpt: dpt,
      path: page.path,
      icon: subpageEdit.value.icon,
      name: subpageEdit.value.name,
      subpage: subpageEdit.value.path,
      // new_subpage: subpageEdit.value.new_subpage  // Optional: New subpage if provided
    });

    if (response.status === 200) {
      // Update the subpage in the UI after a successful API call
      const pages = pagesList.value.find(pages => pages.dpt === dpt);
      const pageToUpdate = pages.pages.find(p => p.path === page.path);
      const subpageToUpdate = pageToUpdate.subpages.find(sub => sub.path === subpageEdit.value.path);

      if (subpageToUpdate) {
        subpageToUpdate.icon = subpageEdit.value.icon;
        subpageToUpdate.name = subpageEdit.value.name;
        subpageToUpdate.path = subpageEdit.value.new_subpage || subpageEdit.value.path;
      }

      editingSubpage.value = false;
      subpageEdit.value = {};
      discardEditSubpage();  // Reset the form on successful save
      getPages()

    }
  } catch (error) {
    console.error(error)
    notifyUser({ icon: "error", message: error.response.data.error, color: "red", position: "bottom", timeout: 2500 });
  }
};

const discardEditSubpage = () => {
  editingSubpage.value = false;
  subpageEdit.value = {};
};

const deleteSubpage = async (dpt, page, subpage) => {
  try {
    const response = await api.delete('/admin/delete-subpage', {
      data: {
        dpt: dpt,
        path: page.path,
        subpage: subpage.path
      }
    })
    if (response.status === 200) {
      page.subpages = page.subpages.filter(p => p.path !== subpage.path)
      getPages()
    }
    else {
      notifyUser({ icon: "error", message: response.data.error, color: "red", position: "bottom", timeout: 2500 })
    }
  }
  catch (error) {
    notifyUser({ icon: "error", message: error.response.data.error, color: "red", position: "bottom", timeout: 2500 })
  }
}

const reorderSubpages = async (dpt, path) => {
   try {
    const response = await api.post('/admin/reorder-subpages', {
      dpt: dpt,
      path: path,
      subpages: pagesList.value.find(pages => pages.dpt === dpt)['pages'].find(pages => pages.path === path)['subpages']
    });
    if (response.status === 200) {
      notifyUser({ icon: "check", message: "Pages reorganisées.", color: "green", position: "bottom", timeout: 2500 })
      getPages()
    }
    else {
      notifyUser({ icon: "error", message: response.data.error, color: "red", position: "bottom", timeout: 2500 })
    }
  }
  catch (error) {
    notifyUser({ icon: "error", message: error.response.data.error, color: "red", position: "bottom", timeout: 2500 })
  }
}


onMounted(async () => {
  loading.value = true
  try {
    const response = await api.get(`/admin/pages?role=${decodedUser.role}&dpt=${decodedUser.dpt}`);
    pagesList.value = response.data
    loading.value = false
  } catch (error) {
    notifyUser({ icon: "error", message: "Erreur lors de la récupération des pages.", color: "red", position: "bottom", timeout: 2500 })
    loading.value = false
  }


})





</script>

<style scoped>
.container {
  width: 80%;
  margin: 1em auto;
  /* background: white; */
}

.actions-bar {
  display: flex;
  flex-wrap: wrap;
  gap: 1em;
  width: 100%;
}

.page-expansion-item,
.subpage-expansion-item {
  width: 80%;
  font-weight: bold;
  background: white;
  margin: auto;
  padding: 0.5em;
}

.subpage-expansion-item {
  margin: auto 0;
  padding: 0;
}


.page-item,
.subpage-item {
  width: 100%;
  display: flex;
  gap: 1em;
  flex-wrap: wrap;
}

.subpage-item {
  width: 80%;
  margin: auto;
}

.page-icon,
.subpage-icon {
  color: var(--sad-nightblue);
  padding: 16px 8px;
}

.page-handle,
.subpage-handle {
  color: var(--sad-nightblue);
  padding: 22px 8px;
  cursor: grab;

}

.page-name,
.subpage-name {
  font-weight: bold;
  color: var(--sad-nightblue);
  padding: 16px;
}

.page-actions,
.subpage-actions,
.new-page-actions,
.new-subpage-actions,
.edit-page-actions,
.edit-subpage-actions {
  opacity: 0;
  width: min-content;
  display: flex;
  gap: 1em;
  margin: auto 5px auto auto;
  height: min-content;
  transition: all 0.3s ease;
}

.new-subpage-actions,
.new-page-actions,
.edit-page-actions,
.edit-subpage-actions {
  opacity: 1;
}

.subpage-item:hover .subpage-actions,
.page-item:hover .page-actions {
  opacity: 1;
}

.new-subpage-form,
.new-page-form,
.edit-page-form,
.edit-subpage-form {
  display: flex;
  align-items: center;
  gap: 1em;
  width: 80%;
  margin: 1em auto;
}
</style>
