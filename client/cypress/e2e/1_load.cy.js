describe('load files', () => {
  it('upload files', () => {
    cy.visit('/')
    cy.get('#btnImport').click();
    const fileName = ['./cypress/fixtures/10469527483063392000-cs_nlp_2301.09640.pdf','./cypress/fixtures/51172457010912950000-prob_2301.09751.pdf']
    cy.get('div > .custom-file-upload').click().selectFile(fileName);
    cy.get('.btn-success').click();
    cy.get('.btn-success').click();
  }),
  it('upload backend workspace', () => {
    cy.visit('/')
    cy.get('#btnImport').click();
    cy.get('#tabWorkspace___BV_tab_button__').click();
    const fileName = ['./cypress/fixtures/asr-VDI_ApplicationStateData_v0.2.1_20240710_0-6.gz']
    cy.get('form > .custom-file-upload').click().selectFile(fileName);
    cy.get('#import-modal___BV_modal_footer_ > div > .btn').click();
  })
})