export async function getConsumptionData(id) {
  let response;
  if (window.location.href.endsWith("summary/")) {
    response = await fetch(`${window.location.origin}/api/summary/`);
  } else {
    response = await fetch(
      `${window.location.origin}/api/detail_search/find/?id_search=${id}`,
    );
  }
  try {
    if (response.ok) {
      const json = await response.json();
      return json;
    }
  } catch (error) {
    console.log(error);
  }
}
