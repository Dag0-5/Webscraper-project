<script setup>
import Header from './components/Header.vue';
import Footer from './components/Footer.vue';
import ProductTable from './components/Table.vue';
</script>

<template>
  <Header/>
  <Footer/>
  <ProductTable
    api-url="http://localhost:5000/search"
    search-item="Shocq Triumph Recurve Limbs"
    category="recurve_limbs"
   />
</template>

<style scoped>
</style>