<script setup>
import {ref} from 'vue'
const emoji = ref('🏹')
</script>

<template>
    <header>
        <span>Archery equipment</span>
        <span>{{emoji}}</span>
    </header>
</template>

<style scoped>
    span{
        font-size:3rem;
        display: table;
        margin: 0 auto;
    }

</style>