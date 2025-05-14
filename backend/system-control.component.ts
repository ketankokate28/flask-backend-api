import { Component, OnInit } from '@angular/core';
import { SystemControlService } from '../../services/system-control.service';
import { AuthService } from '../../services/auth.service';

@Component({
  selector: 'app-system-control',
  templateUrl: './system-control.component.html',
  styleUrls: ['./system-control.component.scss']
})
export class SystemControlComponent implements OnInit {
  running = false;
  loading = false;
  isAdmin = false;

  constructor(
    private svc: SystemControlService,
    private auth: AuthService
  ) {}

  ngOnInit(): void {
    this.isAdmin = this.auth.isAdmin();
    this.refreshStatus();
  }

  refreshStatus(): void {
    this.svc.getStatus().subscribe(res => this.running = res.running);
  }

  toggle(): void {
    if (!this.isAdmin) { return; }
    this.loading = true;
    const op = this.running ? this.svc.stopSystem() : this.svc.startSystem();
    op.subscribe({
      next: () => {
        this.running = !this.running;
        this.loading = false;
      },
      error: () => {
        // TODO: show error notification
        this.loading = false;
      }
    });
  }
}