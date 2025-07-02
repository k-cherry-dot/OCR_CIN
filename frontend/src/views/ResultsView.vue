<template>
  <div class="p-6 space-y-6">
    <h1 class="text-3xl font-bold">Résultats</h1>

    <div v-if="error" class="text-red-600">{{ error }}</div>

    <div v-else-if="!loaded">
      Chargement…
    </div>

    <div v-else>
      <h2 class="text-xl font-semibold">Extracted data</h2>
      <ul class="list-disc list-inside">
        <li>Card number: {{ result.card_number }}</li>
        <li>Surname: {{ result.surname }}</li>
        <li>Given names: {{ result.given_names }}</li>
        <li>Date of birth: {{ result.date_of_birth }}</li>
        <li>Gender: {{ result.gender }}</li>
      </ul>

      <h2 class="text-xl font-semibold mt-4">Comparison</h2>
      <ul class="list-disc list-inside">
        <li v-for="(matched, field) in result.matches" :key="field">
          {{ field }}:
          <span v-if="matched" class="text-green-600">✓</span>
          <span v-else class="text-red-600">✕</span>
          (score: {{ result.similarity_scores[field].toFixed(2) }})
        </li>
      </ul>

      <div v-if="result.issues_found?.length" class="mt-4">
        <h3 class="font-semibold">Issues</h3>
        <ul class="list-disc list-inside text-yellow-700">
          <li v-for="(issue, i) in result.issues_found" :key="i">{{ issue }}</li>
        </ul>
      </div>

      <a
        v-if="result.report_url"
        :href="result.report_url"
        class="inline-block mt-6 px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
        download
      >
        Télécharger le rapport Excel
      </a>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'

const route    = useRoute()
const router   = useRouter()
const resultId = route.query.resultId

const loaded = ref(false)
const result = ref(null)
const error  = ref(null)

if (!resultId) {
  // no id → bounce back
  router.replace({ name: 'Upload' })
}

onMounted(async () => {
  try {
    const res = await fetch(`/api/results/${resultId}`)
    if (!res.ok) {
      const body = await res.json().catch(() => ({}))
      throw new Error(body.error || `HTTP ${res.status}`)
    }
    const body = await res.json()
    result.value = body.data || body   // depending on your route shape
    loaded.value = true
  } catch (e) {
    error.value = e.message
  }
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
