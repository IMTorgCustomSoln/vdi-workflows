<template>
    <div style="height: 100%" >
        <VList :data="getSnippets()" :style="{ height: '100%', padding: '10px' }" #default="item">
            <div 
                v-html="item.indexed_snippet" 
                class="snippet" 
                @click="selectSnippetPage(item.idx, item.snippet)" 
                style="padding-bottom: 15px;"
                >
            </div>
        </VList>
    </div>
</template>

<script>
import { toRaw } from "vue";
import { VList } from "virtua/vue";

import { mapStores } from 'pinia'
import { useUserContent } from '@/stores/UserContent'


export default {
    name: 'SnippetsScroll',
    components: {
        VList
    },
    props: {
        snippets: Array
    },
    data() {
        return {}
    },
    computed: {
        ...mapStores(useUserContent),
    },
    methods: {
        addIndexToSnippetHtml(html, index) {
            return `${html.slice(0, 3)}${index + 1} - ${html.slice(3)}`
        },
        getSnippets() {
            const arr = toRaw(this.snippets)
            const results = []
            for (const [index, snippet] of arr.entries()) {
                const modified_snippet = this.addIndexToSnippetHtml(snippet, index)
                const record = { 
                    idx: index, 
                    snippet: snippet,
                    indexed_snippet: modified_snippet
                }
                results.push(record)
            }
            return results
        },
        selectSnippetPage(id, snippet) {
            //const mouseOverSnippet = `${id}-${snippet}`
            const mouseOverSnippet = { id: id, snippet: snippet }
            //this.searchResults = {...this.searchResults, mouseOverSnippet: mouseOverSnippet}
            this.mouseOverSnippet = mouseOverSnippet
            this.userContentStore.selectedSnippet = mouseOverSnippet        //TODO:change to object and move data extraction from PdfViewer to here: tgtPage, tgtText
        },
    }
}
</script>

<style scoped>
#index {
    padding-right: 7px;
    font-weight: bold;
}

#loader {
    /* 
    display: flex;
    flex-direction: column;
    align-items: left;
    gap: 10px;
    padding: 20px;
    margin: 20px auto 20px auto;
    max-width: 400px;*/

    max-height: calc(100vh - 50px - 200px);
    /*TODO:make more accurate*/
    overflow-y: scroll;
}

/*
.result {
    font-weight: 300;
    width: 80%;
    padding: 20px;
    text-align: center;
    background: #eceef0;
    border-radius: 10px;
}*/
</style>