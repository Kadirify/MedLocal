import { Module } from '@nestjs/common';
import { ConfigModule } from './config/config.module.js';
import { LabReportModule } from './modules/lab-report/lab-report.module.js';

@Module({ imports: [ConfigModule, LabReportModule] })
export class AppModule {}
