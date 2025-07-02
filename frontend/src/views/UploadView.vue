<template>
  <div class="container">
    <h1 class="title">Nouvelle session</h1>
    <CsvUploader @uploaded="onCsv" />
    <PdfUploader v-if="uploadId" :uploadId="uploadId" @uploaded="onPdf" />
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'

import CsvUploader from '../components/CsvUploader.vue'
import PdfUploader from '../components/PdfUploader.vue'

const router = useRouter()
const uploadId = ref(null)

function onCsv(id) {
  uploadId.value = id
}

function onPdf(id) {
  fetch(`/api/process/${id}`, { method: 'POST' })
    .then(r => r.json())
    .then(data => {
      router.push({ name: 'Results', query: { resultId: data.result_id } })
    })
}
</script>

<style scoped>
.container {
  padding: 20px;
  max-width: 800px;
  margin: 0 auto;
}

.title {
  font-size: 2rem;
  font-weight: bold;
  margin-bottom: 20px;
}

button {
  padding: 12px 24px;
  background-color: #007BFF;
  color: white;
  border: none;
  cursor: pointer;
  border-radius: 5px;
}

button:hover {
  background-color: #0056b3;
}
</style>
