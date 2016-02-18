# task-list
Mac native Python app for task management

Like a Pomodoro, it goes for a set amount of time "on task", then a set amount of time on break.  It's much less formal, though.

It starts with a hierarchy of tasks, provided by sources, for example RedmineSource loads a given user's tasks from [Redmine](http://www.redmine.org/).

When the time is up, or the break is up, it raises an alert.  Currently that is a modal dialog, which should

* Not interfere with the keyboard/mouse focus
* Cause the app icon to bounce in the dock

I hated all the alerts in apps I saw, this was the main reason I started this project.  This still isn't great, the only notification is the bouncing dock icon, which isn't really sticky.  It doesn't interfere with your work, but that also means it's easy to just keep working.  So a lot of the work has been on the snooze.

There are two levels of snooze:

When the app alarms, the user can choose to extend the existing work (or break) period for a short period of time.

If the user ignores the alarm itself, the app raises another alarm. It stops at that point, since the user may have stepped away from the keyboard for a while.  This could be done much better.
