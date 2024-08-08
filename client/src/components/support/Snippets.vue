<template>
    <div id="loader">
        <div class="result" v-for="(snippet, index) in loaded_snippets">
            <div class="snippet" @click="selectSnippetPage(index, snippet)">
                <div v-html="snippet"></div>
            </div>
            <br />
        </div>
        <infinite-loading target="#loader" @infinite="load"></infinite-loading>
    </div>
</template>




<script>
import { toRaw } from "vue";
import InfiniteLoading from "v3-infinite-loading";
import "v3-infinite-loading/lib/style.css";

import { mapStores } from 'pinia'
import { useUserContent } from '@/stores/UserContent'


export default {
    name: 'SnippetsScroll',
    components: {
        InfiniteLoading
    },
    props: {
        snippets: Array
    },
    data() {
        return {
            loaded_snippets: [],
            batch: 1
        }
    },
    computed: {
        ...mapStores(useUserContent),

    },
    methods: {
        getSnippets(batch) {
            const page = batch * 10
            const arr = toRaw(this.snippets)
            const results = []
            for (const [index, snippet] of arr.entries()) {
                if (index < page) {
                //if (index < page && index >= page - 10) {
                    results.push(snippet)
                }
            }
            return results
        },
        load($state) {
            console.log("loading...");
            try {
                const snippets = this.getSnippets(this.batch)
                if (snippets.length < 10) $state.complete();
                else if(this.loaded_snippets.length >= this.snippets.length) $state.loaded();
                else {
                    this.loaded_snippets.length = 0
                    this.loaded_snippets.push(...snippets);
                    $state.loaded();
                }
                this.batch++;
            } catch (error) {
                $state.error();
            }
        },
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

<style>

#loader {
    /*
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 10px;
    padding: 20px;
    margin: 20px auto 20px auto;
    max-width: 400px;
    */
    max-height: calc(100vh - 50px - 200px);
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