<template>
    <b-icon-question-circle class="h5 mb-2" font-scale=".75" :variant="variantColor" @click="toggleModal"/>

    <b-modal 
        :id="$props.id"  
        :title="title"
        centered
        hide-footer
        >
        <div class="my-4" v-html="this.htmlText"></div>
    </b-modal>
</template>


<script>
export default{
    name: 'Guide',
    props: ['id', 'title', 'markdown', 'variantCustom'],
    data(){
        return{
            title:'',
            htmlText:''
        }
    },
    computed:{
        variantColor(){return this.$props.variantCustom!=undefined ? null : 'primary'}
    },
    methods:{
        toggleModal() {
            const id = this.$props.id
            this.setTitle()
            this.setHtml(this.$props.markdown)
            this.$bvModal.show(id)
        },
        setTitle(){
            this.title = `Guide: ${this.$props.title}`
        },
        setHtml(markdown){
            this.htmlText = marked.parse(markdown)
        },
    }
}
</script>