export async function getConsumptionData(id) {
  let response;
  if (window.location.href == "http://127.0.0.1:8000/summary/") {
    response = await fetch("http://127.0.0.1:8000/api/summary/");
  } else {
    response = await fetch(
      `http://127.0.0.1:8000/api/detail_search/find/?id_search=${id}`,
    );
  }
  try {
    if (response.ok) {
      const json = await response.json();
      return json;
    }
  } catch (error) {
    console.log(error);
  }ßßß
}
