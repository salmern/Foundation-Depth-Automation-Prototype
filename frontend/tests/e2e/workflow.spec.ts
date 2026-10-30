import {test,expect} from '@playwright/test';
import path from 'node:path';
import {execFileSync} from 'node:child_process';
const fixture=path.resolve('../backend/tests/fixtures');
test('real API: sources, processing, calculation trace, issues and review workbook',async({page})=>{
 await page.goto('/');await page.getByLabel('Project name').fill(`Browser integration ${Date.now()}`);await page.getByRole('button',{name:'Create project'}).click();await expect(page).toHaveURL(/\/projects\/[a-f0-9]{32}/);
 for(const [category,file] of [['foundation',path.join(fixture,'synthetic-house.dxf')],['reviewed_inputs',path.join(fixture,'synthetic-reviewed-inputs.json')],['template',path.resolve('../../2 Template/MASTER Foundation Schedule.xlsx')]]){
  await page.getByLabel('File purpose').selectOption(category);await page.getByLabel('Choose source files').setInputFiles(file);await expect(page.getByRole('cell',{name:'container validated',exact:true})).toHaveCount(category==='foundation'?1:category==='reviewed_inputs'?2:3);
 }
 await page.getByRole('button',{name:'Continue to processing'}).click();await page.getByRole('button',{name:'Start processing'}).click();await expect(page.getByText('Run status: completed with issues.',{exact:false})).toBeVisible({timeout:90000});
 await page.getByRole('button',{name:'Extraction',exact:false}).click();await expect(page.getByText('5 records · first 100 per page')).toBeVisible();
 await page.getByRole('button',{name:'Calculations',exact:false}).click();await expect(page.getByRole('cell',{name:'97.950',exact:true})).toBeVisible();await page.getByRole('button',{name:'View calculation'}).first().click();await expect(page.getByRole('dialog')).toContainText('45 degree influence');await page.getByRole('button',{name:'Close calculation detail'}).click();
 await page.getByRole('button',{name:'Review issues',exact:false}).click();await page.getByLabel('Severity').selectOption('error');await expect(page.getByRole('heading',{name:/Complete schedule export is blocked/})).toBeVisible();
 await page.getByRole('button',{name:'Outputs',exact:false}).click();const pending=page.waitForEvent('download');await page.getByRole('article').filter({hasText:'foundation-draft-schedule.xlsx'}).getByRole('button',{name:'Download'}).click();const download=await pending;const saved=await download.path();expect(saved).toBeTruthy();
 execFileSync(path.resolve('../.venv/bin/python'),['-c','import openpyxl,sys; w=openpyxl.load_workbook(sys.argv[1]); assert "Automation Review" in w.sheetnames; assert w["Generic 4 corner output"]["U10"].value == 97.95',saved!]);
});
