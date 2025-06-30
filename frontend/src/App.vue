<template>
  <div class="p-4">
    <h1 class="text-2xl font-bold mb-4">OCR CIN Platform</h1>
    <CsvUploader @uploaded="handleUpload" />
    <PdfUploader v-if="uploadId" :uploadId="uploadId" @uploaded="handlePdfUpload" />
    <ResultsTable v-if="processedId" :uploadId="uploadId" />
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
