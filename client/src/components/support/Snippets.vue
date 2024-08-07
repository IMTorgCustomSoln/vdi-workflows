<template>
    <div id="loader">
    <div v-for="(snippet, index) in snippets">
        <div class="snippet" @click="selectSnippetPage(index, snippet)">
            <div v-html="snippet"></div>
        </div>
        <br />
    </div>
    <infinite-loading target="#loader" @infinite="load"></infinite-loading>
</div>
</template>

<script>
import InfiniteLoading from "v3-infinite-loading";
import "v3-infinite-loading/lib/style.css";

import { mapStores } from 'pinia'
import { useUserContent } from '@/stores/UserContent'


export default {
    name: 'SnippetsScroll',
    components:{
        InfiniteLoading
    },
    props: {
        snippets: Array
    },
    data() {
        return {
            start: 0
        }
    },
    computed: {
        ...mapStores(useUserContent),
    },
    methods: {
        selectSnippetPage(id, snippet) {
            //const mouseOverSnippet = `${id}-${snippet}`
            const mouseOverSnippet = { id: id, snippet: snippet }
            //this.searchResults = {...this.searchResults, mouseOverSnippet: mouseOverSnippet}
            this.mouseOverSnippet = mouseOverSnippet
            this.userContentStore.selectedSnippet = mouseOverSnippet
        },
    }
}

</script>