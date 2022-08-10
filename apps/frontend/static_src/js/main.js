import { Dropdown } from 'bootstrap';

const searchInput = document.getElementById("search-input")
const searchIconButton = document.getElementById("search-icon-button")

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
searchInput.addEventListener("keyup", onSearchInputChange)


const removeExistingChildren = (parent) => {
    const children = [...parent.children]
    for (const child of children) {
        child.remove()
    }
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

    for(const result of results) {
        const resultDiv = document.createElement("div")
        const resultLink = document.createElement("a")
        const resultDescription = document.createElement("div")
        const resultParentSection = document.createElement("div")
        resultLink.appendChild(document.createTextNode(result.title))
        resultDescription.appendChild(document.createTextNode(result.search_description))
        resultParentSection.appendChild(document.createTextNode(result.parent_section))
        resultLink.href = result.url_path.replace('home-x/', '').replace('home-x-', '')
        resultDiv.appendChild(resultParentSection)
        resultDiv.appendChild(resultLink)
        resultDiv.appendChild(resultDescription)
        resultParentSection.classList.add('py-2')
        resultLink.classList.add('fw-bold', 'fs-5', 'text-decoration-none', 'text-dark')
        resultDescription.classList.add('text-muted', 'py-2')
        resultDiv.classList.add('mx-5', 'py-4', 'border-top', 'border-bottom')
        resultsDiv.appendChild(resultDiv)
    }
    
}
