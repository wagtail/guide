// NOTE: A 'Cache Level' page rule set to 'Cache Everything' will
// prevent private cookie cache skipping from working, as it is
// applied after this worker runs.

// When any cookie in this list is present in the request, cache will be skipped
const PRIVATE_COOKIES = ["csrftoken", "sessionid"];

// These querystring keys are stripped from the request as they are generally not
// needed by the origin.
const STRIP_QUERYSTRING_KEYS = [
    "utm_source",
    "utm_campaign",
    "utm_medium",
    "utm_term",
    "utm_content",
    "gclid",
    "fbclid",
    "dm_i", // DotDigital
    "msclkid",
];

// If this is true, the querystring keys stripped from the request will be
// addeed to any Location header served by a redirect.
const REPLACE_STRIPPED_QUERYSTRING_ON_REDIRECT_LOCATION = false

// If this is true, querystring key are stripped if they have no value eg. ?foo
// Disabled by default, but highly recommended
const STRIP_VALUELESS_QUERYSTRING_KEYS = false;

// Only these status codes should be considered cacheable
// (from https://www.w3.org/Protocols/rfc2616/rfc2616-sec13.html#sec13.4)
const CACHABLE_HTTP_STATUS_CODES = [200, 203, 206, 300, 301, 410];

addEventListener("fetch", (event) => {
    event.respondWith(main(event));
});

async function main(event) {
    const cache = caches.default;
    let request = event.request;
    let strippedParams;
    [request, strippedParams] = stripQuerystring(request);

    if (!requestIsCachable(request)) {
        // If the request isn't cacheable, return a Response directly from the origin.
        return fetch(request);
    }

    let response = await cache.match(request);

    if (!response) {
        // If we didn't get a response from the cache, fetch one from the origin
        // and put it in the cache.
        response = await fetch(request);
        if (responseIsCachable(response)) {
            event.waitUntil(cache.put(request, response.clone()));
        }
    }

    if (REPLACE_STRIPPED_QUERYSTRING_ON_REDIRECT_LOCATION) {
        response = replaceStrippedQsOnRedirectResponse(response, strippedParams);
    }

    return response;
}

/*
 * Cacheability Utilities
 */
function requestIsCachable(request) {
    /*
     * Given a Request, determine if it should be cached.
     * Currently the only factor here is whether a private cookie is present.
     */
    return !hasPrivateCookie(request)
}

function responseIsCachable(response) {
    /*
     * Given a Response, determine if it should be cached.
     * Currently the only factor here is whether the status code is cachable.
     */
    return CACHABLE_HTTP_STATUS_CODES.includes(response.status)
}


/*
 * Request Utilities
 */
function stripQuerystring(request) {
    /**
     * Given a Request, return a new Request with the ignored or blank querystring keys stripped out,
     * along with an object representing the stripped values.
     */
    const url = new URL(request.url);

    const stripKeys = STRIP_QUERYSTRING_KEYS.filter((v) =>
        url.searchParams.has(v),
    );

    let strippedParams = {};

    if (stripKeys.length) {
        stripKeys.reduce((acc, key) => {
            acc[key] = url.searchParams.getAll(key);
            url.searchParams.delete(key);
            return acc;
        }, strippedParams);
    }

    if (STRIP_VALUELESS_QUERYSTRING_KEYS) {
        // Strip query params without values to avoid unnecessary cache misses
        for (const [key, value] of url.searchParams.entries()) {
            if (!value) {
                url.searchParams.delete(key);
                strippedParams[key] = '';
            }
        }
    }

    return [new Request(url, request), strippedParams];
}

function hasPrivateCookie(request) {
    /*
     * Given a Request, determine if one of the 'private' cookies are present.
     */
    const cookieHeader = request.headers.get("Cookie");
    if (!cookieHeader) {
        return false;
    }

    const requestCookieNames = cookieHeader
        .split(";")
        .map((cookie) => cookie.split("=")[0].trim());

    return PRIVATE_COOKIES.some((privateCookieName) =>
        requestCookieNames.includes(privateCookieName)
    );
}

/**
 * Response Utilities
 */

function replaceStrippedQsOnRedirectResponse(response, strippedParams) {
    /**
     * Given an existing Response, and an object of stripped querystring keys,
     * determine if the response is a redirect.
     * If it is, add the stripped querystrings to the location header.
     * This allows us to persist tracking querystrings (like UTM) over redirects.
     */
    response = new Response(response.body, response);

    if ([301, 302].includes(response.status)) {
        const locationHeaderValue = response.headers.get("location");
        let locationUrl;

        if (!locationHeaderValue) {
            return response;
        }

        const isAbsolute = isUrlAbsolute(locationHeaderValue);

        if (!isAbsolute) {
            // If the Location URL isn't absolute, we need to provide a Host so we can use
            // a URL object.
            locationUrl = new URL(locationHeaderValue, "http://www.example.com");
        } else {
            locationUrl = new URL(locationHeaderValue)
        }

        for (const [key, value] of Object.entries(strippedParams)) {
            locationUrl.searchParams.append(key, value);
        }

        let newLocation;

        if (isAbsolute) {
            newLocation = locationUrl.toString()
        } else {
            newLocation = `${locationUrl.pathname}${locationUrl.search}`;
        }

        response.headers.set("location", newLocation);
    }

    return response
}

/**
 * URL Utilities
 */
function isUrlAbsolute(url) {
    return (url.indexOf('://') > 0 || url.indexOf('//') === 0);
}
