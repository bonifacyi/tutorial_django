(function(){
	if (window.myBookmarklet !== undefined){
		myBookmarklet();
	}
	else {
		console.log('qwe');
		document.body.appendChild(
			document.createElement('script')
		).src='http://127.0.0.1:8000/static/js/bookmarklet.js?k=' +
			Math.floor(Math.random()*99999999999999999999);
	}
})();