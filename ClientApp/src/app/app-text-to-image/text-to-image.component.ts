import {Component, ViewChild} from '@angular/core';

@Component({
  selector: 'app-text-to-image',
  templateUrl: './text-to-image.component.html',
})
export class TextToImageComponent {

  @ViewChild('promptTextBox') promptTextBoxRef : HTMLTextAreaElement = new HTMLTextAreaElement();

  public imageSource: string = '';

  
}
