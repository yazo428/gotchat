import { resolveDateTime } from "./api";
import { CalendarComponent } from "./calendarComponent";
import "./style.css";
const input = document.querySelector<HTMLInputElement>("#text-input")!;
const button = document.querySelector<HTMLButtonElement>("#submit-button")!;
const resultDiv = document.querySelector<HTMLDivElement>("#result")!;

const calendarEl = document.getElementById("calendar")!;
const calendarComponent = new CalendarComponent(calendarEl);

button.addEventListener("click", async () => {
  const data = await resolveDateTime(input.value);
  for(let i=0;i<data.results.length; i++){
    const { start, end } = data.results[i];
    calendarComponent.addEvent(start, end);

    resultDiv.insertAdjacentHTML("beforeend",`${start}〜${end}に予定を追加しました`)
  }
});
