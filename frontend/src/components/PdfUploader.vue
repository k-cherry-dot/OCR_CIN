<template>
  <div class="mb-4">
    <label class="block mb-2">Upload CIN PDF:</label>
    <input type="file" @change="onFileChange" accept=".pdf" class="border p-2" />
  </div>
</template>

<script>
import axios from 'axios';
export default {
  props: ['uploadId'],
  emits: ['uploaded'],
  methods: {
    onFileChange(e) {
      const file = e.target.files[0];
      const form = new FormData();
      form.append('upload_id', this.uploadId);
      form.append('file', file);
      axios.post('/api/uploads/pdf', form)
        .then(res => this.$emit('uploaded', res.data.upload_id));
    }
  }
};
</script>
