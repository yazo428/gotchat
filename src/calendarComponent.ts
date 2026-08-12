import { Calendar } from "fullcalendar";
import themePlugin from "fullcalendar/themes/monarch";
import dayGridPlugin from "fullcalendar/daygrid";
import timeGridPlugin from "fullcalendar/timegrid";

import "fullcalendar/skeleton.css";
import "fullcalendar/themes/monarch/theme.css";
import "fullcalendar/themes/monarch/palettes/purple.css";

export class CalendarComponent {
  private calendar: Calendar;

  constructor(container: HTMLElement) {
    this.calendar = new Calendar(container, {
      plugins: [themePlugin, dayGridPlugin, timeGridPlugin],
      initialView: "dayGridMonth",
      aspectRatio:1.1,
      headerToolbar: {
        left: "prev,next today",
        center: "title",
        right: "dayGridMonth,timeGridWeek",
      },
    });
    this.calendar.render();
  }

  addEvent(start: string, end: string) {
    this.calendar.addEvent({
      title: "候補",
      start,
      end,
    });
  }
}
