<template>
  <div class="flex flex-col min-h-screen">
    <!-- Header -->
    <header class="bg-blue-800 text-white p-4 shadow">
      <div class="container mx-auto flex justify-between items-center">
        <h1 class="text-3xl font-bold">OCR CIN Platform</h1>
        <nav>
          <!-- you can add nav links here if needed -->
        </nav>
      </div>
    </header>

    <!-- Main content -->
    <main class="flex-1 container mx-auto p-6 space-y-6">
      <CsvUploader @uploaded="handleUpload" />
      <PdfUploader
        v-if="uploadId"
        :uploadId="uploadId"
        @uploaded="handlePdfUpload"
      />
      <ResultsTable v-if="processedId" :uploadId="uploadId" />
    </main>

    <!-- Footer -->
    <footer class="bg-gray-100 text-gray-700 text-sm text-center p-4">
      <div class="container mx-auto">
        © 2025 Ecole Centrale Casablanca – Tous droits réservés
      </div>
    </footer>
  </div>
</template>

<script>
import { ref } from 'vue';
import CsvUploader from './components/CsvUploader.vue';
import PdfUploader from './components/PdfUploader.vue';
import ResultsTable from './components/ResultsTable.vue';

export default {
  components: { CsvUploader, PdfUploader, ResultsTable },
  setup() {
    const uploadId = ref(null);
    const processedId = ref(null);

    function handleUpload(id) {
      uploadId.value = id;
    }
    function handlePdfUpload(id) {
      fetch(`/api/process/${id}`, { method: 'POST' })
        .then(res => res.json())
        .then(data => {
          processedId.value = data.result_id;
        });
    }

    return { uploadId, processedId, handleUpload, handlePdfUpload };
  }
};
</script>
