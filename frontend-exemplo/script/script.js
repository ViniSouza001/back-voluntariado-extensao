const form = document.querySelector('form');

const prefixoUrl = "http://127.0.0.1:8000"

const inpNome = document.querySelector('#nome');
const inpEmail = document.querySelector('#email');
const inpSenha = document.querySelector('#senha');
const inpData_nasc = document.querySelector('#data_nasc');
const inpCidade = document.querySelector('#cidade');
const inpUf = document.querySelector('#uf');

const inpResultado = document.querySelector("#resultado")



form.addEventListener("submit", (e) => {
    e.preventDefault();

    enviarForm();
})


const enviarForm = async () => {
    const nome = inpNome.value
    const email = inpEmail.value
    const senha = inpSenha.value
    const data_nasc = inpData_nasc.value
    const cidade = inpCidade.value
    const uf = inpUf.value

    fetch(prefixoUrl + "/auth/register", {
        method: "POST",
        headers: {
            'Content-type': "application/json"
        },
        body: JSON.stringify({
            nome, email, senha, data_nasc, cidade, uf
        })
    })
    .then(response => response.json())
    .then(data => {
        inpResultado.innerText = data.mensagem
    })
}