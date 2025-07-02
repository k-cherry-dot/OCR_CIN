<template>
  <div class="container">
    <h1 class="title">Résultats de la session</h1>
    <p class="description">Here you will see the processed results.</p>
    <!-- Display your results here, such as a table or list -->
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const resultId = ref(route.query.resultId)

onMounted(() => {
  console.log(resultId.value) // Process results based on the resultId query parameter
})
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

.description {
  font-size: 1.2rem;
  color: #555;
  margin-bottom: 30px;
}
</style>
