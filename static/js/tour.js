if (window.location.search === undefined || window.location.search === '') {
    console.log("hello")
    if (document.cookie.split(';').filter((item) => item.includes('tour=')).length) {
        window.location.search = '?tour=' + document.cookie.split(';').filter((item) => item.includes('tour='))[0].split('=')[1];
    }
}