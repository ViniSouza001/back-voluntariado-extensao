const btn = document.querySelector('button')
const prefixoUrl = "http://127.0.0.1:8000"


const pResultado = document.querySelector('#resultado')

btn.addEventListener('click', () => {
    const params = new URLSearchParams (
        window.location.search
    )
    const token = params.get("token")
    
    confirmarConta(token)
})

const confirmarConta = async (token) => {
    await fetch(prefixoUrl + `/auth/confirmar-email/${token}`)
    .then(response => response.json())
    .then(data => {
        console.log(data)
        pResultado.innerText = data.mensagem
    })
}