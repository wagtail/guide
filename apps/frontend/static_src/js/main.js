import { Dropdown } from 'bootstrap';

const search_input = document.getElementById("search_input")
const searchIconButton = document.getElementById("searchIconButton")

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


const removeExistingChildren = (parent) => {
    const children = [...parent.children]
    children.map((child) => {
        child.remove()
    })
}
searchIconButton.addEventListener("click", () => {
    const resultsDiv = document.getElementById("results")
    const resultsCountContainer = document.getElementById("results-count-container")

    removeExistingChildren(resultsDiv)
    removeExistingChildren(resultsCountContainer)
})

const injectResultsInHTML = (results) => {
    const resultsDiv = document.getElementById("results")
    const resultsCountContainer = document.getElementById("results-count-container")

    removeExistingChildren(resultsDiv)
    removeExistingChildren(resultsCountContainer)

    const resultsCountDiv = document.createElement("div")
    const resultsCountData = document.createTextNode(`${results.length} ${results.length == 1 ? 'result' : 'results'} found`)
    resultsCountDiv.appendChild(resultsCountData)
    resultsCountDiv.classList.add('m-3', 'mx-5')
    resultsCountContainer.appendChild(resultsCountDiv)

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
