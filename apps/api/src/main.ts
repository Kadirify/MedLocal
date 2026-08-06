import 'reflect-metadata';
import { existsSync } from 'node:fs';
import { ValidationPipe } from '@nestjs/common';
import { NestFactory } from '@nestjs/core';
import { AppModule } from './app.module.js';
import { AppConfig } from './config/app-config.js';

if (existsSync('.env')) process.loadEnvFile('.env');

const app = await NestFactory.create(AppModule);
const config = app.get(AppConfig);

app.enableCors({ origin: config.webOrigin });
app.useGlobalPipes(new ValidationPipe({ transform: true, whitelist: true }));

await app.listen(config.port, '127.0.0.1');
