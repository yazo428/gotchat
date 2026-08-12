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
  const { start, end } = data.results[0];
  calendarComponent.addEvent(start, end);
});
