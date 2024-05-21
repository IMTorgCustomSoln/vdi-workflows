import { defineStore } from 'pinia'


export const useAppDisplay = defineStore('appDisplay', {
    state: () => {
        return {
            exportAppStateFileName: 'WorkSession.gz',
            api: {
                server: 'http://localhost:8000/api/',
                documentGroup: 'documentgroups/'
            },

            views: {
                viewSelection: 'search',
                viewOptions: [
                    { text: 'Search', value: 'search' },
                    { text: 'Read', value: 'read' },
                    { text: 'Explore', value: 'explore', disabled: true }
                ],
                attrs: { //initialized
                    table: {
                        size: 100,
                        fields: searchTableFields,
                        toggleExpansionBtn: true,
                        colsTable: 12,
                        colsSnippets: 0
                    },
                    pdfViewer: {
                        size: 0
                    }
                }
            }
        }
    },
    getters: {

    },
    actions: {
        viewSelection(checked) {
            if (checked == 'search') {
                this.views.attrs.table.size = 100
                this.views.attrs.table.fields = searchTableFields
                this.views.attrs.table.toggleExpansionBtn = true
                this.views.attrs.pdfViewer.size = 0

                this.views.attrs.table.colsTable = 12
                this.views.attrs.table.colsSnippets = 0
            }
            else if (checked == 'read') {
                this.views.attrs.table.size = 50
                this.views.attrs.table.fields = readTableFields
                this.views.attrs.table.toggleExpansionBtn = false
                this.views.attrs.pdfViewer.size = 50

                this.views.attrs.table.colsTable = 0
                this.views.attrs.table.colsSnippets = 0
            }
        }

    }



})





const searchTableFields = [{
    key: 'sort_key',
    label: 'Score',
    sortable: true,
    sortDirection: 'desc',
    formatter: "getFormattedScore"
}, {
    key: 'id',
    label: 'Id'
}, {
    key: 'reference_number',
    label: 'Reference',
    sortable: true,
}, {
    key: 'filepath',
    label: 'Path',
    sortable: true,
    formatter: "getFormattedPath"
}, {
    key: 'title',
    label: 'Title',
    sortable: true
}, {
    key: 'page_nos',
    label: 'Pages',
    sortable: true
}, {
    key: 'length_lines',
    label: 'Sentences',
    sortable: true
}, {
    key: 'file_size_mb',
    label: 'File Size',
    sortable: true,
    formatter: "getFormattedFileSize"
}, {
    key: 'date',
    sortable: true,
    formatter: "formatDateAssigned"
}]


const readTableFields = [{
    key: 'sort_key',
    label: 'Score',
    sortable: true,
    sortDirection: 'desc',
    formatter: "getFormattedScore"
}, {
    key: 'title',
    label: 'Title',
    sortable: true
},]
