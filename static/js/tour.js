if (window.location.search === undefined || window.location.search === '') {
    console.log("hello")
    if (document.cookie.split(';').filter((item) => item.includes('tour=')).length) {
        let walkthrough = fetch('/static/walkthrough.json').then(response => response.json()).then(
            (data) => {
                let currentUrl = window.location.href;
                let tourCookie = document.cookie.split(';').find((item) => item.includes('tour=')).split('=')[1];

                let tourUrl = data.find((item) => item.tour === tourCookie).url;

                if (!currentUrl.includes(tourUrl)) {
                    window.location.href = `${tourUrl}?tour=${tourCookie}`;
                } else {
                    window.location.href = `?tour=${tourCookie}`;
                }
            });
    }
}