// 가상 API 데이터
const apiData = [
    {
        title: "2024년 상반기 인구 통계 발표",
        link: "https://www.kostat.go.kr/news1",
        date: "2024-12-01"
    },
    {
        title: "경제성장률 최신 통계",
        link: "https://www.kostat.go.kr/news2",
        date: "2024-11-28"
    },
    {
        title: "국내 소비 트렌드 보고서",
        link: "https://www.kostat.go.kr/news3",
        date: "2024-11-20"
    }
];

// DOM 요소 참조
const newsList = document.getElementById("newsList");
const searchBar = document.getElementById("searchBar");

// 뉴스 데이터 렌더링 함수
function renderNews(data) {
    newsList.innerHTML = ""; // 기존 콘텐츠 초기화
    data.forEach(news => {
        const listItem = document.createElement("li");
        listItem.className = "news-item";
        listItem.innerHTML = `
            <a href="${news.link}" target="_blank">${news.title}</a>
            <span>${news.date}</span>
        `;
        newsList.appendChild(listItem);
    });
}

// 검색 필터링 함수
searchBar.addEventListener("input", () => {
    const keyword = searchBar.value.toLowerCase();
    const filteredNews = apiData.filter(news =>
        news.title.toLowerCase().includes(keyword)
    );
    renderNews(filteredNews);
});

// 초기 데이터 렌더링
renderNews(apiData);
