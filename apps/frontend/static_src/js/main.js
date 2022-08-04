import { Dropdown } from 'bootstrap';

const search_input = document.getElementById("search_input")

const onSearchInputChange = async (event) => {
    const query = event.target.value
    try {
        const res = await fetch(window.location.origin + '/search_json/?query=' + query)
        const data = await res.json()
        injectResultsInHTML(data)
    } catch(err) {
        console.log(err)
        return {"error": err}
    }
}
search_input.addEventListener("keyup", onSearchInputChange)


const injectResultsInHTML = (results) => {
    const resultsDiv = document.getElementById("results")
    const resultsCountDiv = document.getElementById("results-count")

    const children = [...resultsDiv.children]
    children.map((child) => {
        child.remove()
    })
    resultsCountDiv.innerText = `${results.length} results found`

    results.map((result) => {
        const resultDiv = document.createElement("div")
        const resultLink = document.createElement("a")
        const data = document.createTextNode(result.title)
        resultLink.appendChild(data)
        const link = result.url_path.replace('home-x/', '').replace('home-x-', '')
        resultLink.href = link
        resultDiv.appendChild(resultLink)
        resultDiv.classList.add('mx-5', 'py-4', 'border-top', 'border-bottom', 'fw-bold', 'fs-5')
        resultsDiv.appendChild(resultDiv)
    })
    
}
