const pNome = document.querySelector("#nome")
const pEmail = document.querySelector("#email")
const pData_nasc = document.querySelector("#data_nasc")
const pCidade = document.querySelector("#cidade")
const pUf = document.querySelector("#uf")

const btnConsultar = document.querySelector("#btnConsultar")


const prefixoUrl = "http://127.0.0.1:8000"

btnConsultar.addEventListener('click', (e) => {
    e.preventDefault()

    consultarDados()
})


const consultarDados = async () => {
    const token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwiZXhwIjoxNzgwNzU4MDgxLCJ0aXBvIjoidXN1YXJpbyJ9.dPNqE-oweEIpgDSlMivDvB5eJniJF8ovo910s-1L5FA"
    const response = await fetch(prefixoUrl + "/user/me", {
        method: "GET",
        headers: {
            'Content-type': "application/json",
            "Authorization": `Bearer ${token}`
        },
    });

    const dados = await response.json()
    console.log(dados)
}